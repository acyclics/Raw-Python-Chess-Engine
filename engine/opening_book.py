"""
    References:
    http://hgm.nubati.net/book_format.html
    https://github.com/niklasf/python-chess/blob/master/chess/polyglot.py
"""
import os
import numpy as np
import struct
import random
import mmap
from types import TracebackType
from typing import Callable, Container, Iterator, List, NamedTuple, Optional, Type, Union

from engine.zobrist_hashing import ZobristHashing


PathLike = Union[str, bytes, os.PathLike]
ENTRY_STRUCT = struct.Struct(">QHHI")
FILE_NAMES = ["a", "b", "c", "d", "e", "f", "g", "h"]
RANK_NAMES = ["1", "2", "3", "4", "5", "6", "7", "8"]
SQUARE_NAMES = [f + r for r in RANK_NAMES for f in FILE_NAMES]


class Entry(NamedTuple):
    """An entry from a Polyglot opening book."""

    key: int
    """The Zobrist hash of the position."""

    move_name: str
    """Name of move."""

    raw_move: int
    """
    The raw binary representation of the move. Use
    :data:`~chess.polyglot.Entry.move` instead.
    """

    weight: int
    """An integer value that can be used as the weight for this entry."""

    learn: int
    """Another integer value that can be used for extra information."""


class _EmptyMmap(bytearray):
    def size(self) -> int:
        return 0

    def close(self) -> None:
        pass


def _randint(rng: Optional[random.Random], a: int, b: int) -> int:
    return random.randint(a, b) if rng is None else rng.randint(a, b)


class MemoryMappedReader:
    """Maps a Polyglot opening book to memory."""

    def __init__(self, filename: PathLike) -> None:
        self.fd = os.open(filename, os.O_RDONLY | os.O_BINARY if hasattr(os, "O_BINARY") else os.O_RDONLY)
        self.zobrist = ZobristHashing()

        try:
            self.mmap: Union[mmap.mmap, _EmptyMmap] = mmap.mmap(self.fd, 0, access=mmap.ACCESS_READ)
        except (ValueError, OSError):
            self.mmap = _EmptyMmap()  # Workaround for empty opening books.

        if self.mmap.size() % ENTRY_STRUCT.size != 0:
            raise IOError(f"invalid file size: ensure {filename!r} is a valid polyglot opening book")

        try:
            # Python 3.8
            self.mmap.madvise(mmap.MADV_RANDOM)  # type: ignore
        except AttributeError:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_value: Optional[BaseException], traceback: Optional[TracebackType]) -> None:
        return self.close()

    def __len__(self) -> int:
        return self.mmap.size() // ENTRY_STRUCT.size

    def __getitem__(self, index: int) -> Entry:
        if index < 0:
            index = len(self) + index

        try:
            key, raw_move, weight, learn = ENTRY_STRUCT.unpack_from(self.mmap, index * ENTRY_STRUCT.size)
        except struct.error:
            raise IndexError()

        # Extract source and target square.
        to_square = raw_move & 0x3f
        from_square = (raw_move >> 6) & 0x3f

        move_name = SQUARE_NAMES[from_square] + SQUARE_NAMES[to_square]

        # Extract the promotion type.
        promotion_part = (raw_move >> 12) & 0x7
        promotion = promotion_part + 1 if promotion_part else None

        # Piece drop.
        if from_square == to_square:
            promotion, drop = None, promotion
        else:
            drop = None

        return Entry(key, move_name, raw_move, weight, learn)

    def __iter__(self) -> Iterator[Entry]:
        i = 0
        size = len(self)
        while i < size:
            yield self[i]
            i += 1

    def bisect_key_left(self, key: int) -> int:
        lo = 0
        hi = len(self)

        while lo < hi:
            mid = (lo + hi) // 2
            mid_key, _, _, _ = ENTRY_STRUCT.unpack_from(self.mmap, mid * ENTRY_STRUCT.size)
            if mid_key < key:
                lo = mid + 1
            else:
                hi = mid

        return lo

    def __contains__(self, entry: Entry) -> bool:
        return any(current == entry for current in self.find_all(entry.key, minimum_weight=entry.weight))

    def find_all(self, game, *, minimum_weight: int = 1) -> Iterator[Entry]:
        """Seeks a specific position and yields corresponding entries."""
        key = self.zobrist.hash(game)

        i = self.bisect_key_left(key)
        size = len(self)

        while i < size:
            entry = self[i]
            i += 1

            if entry.key != key:
                break

            if entry.weight < minimum_weight:
                continue

            yield entry

    def find(self, game, *, minimum_weight: int = 1) -> Entry:
        """
        Finds the main entry for the given position or Zobrist hash.
        The main entry is the (first) entry with the highest weight.
        By default, entries with weight ``0`` are excluded. This is a common
        way to delete entries from an opening book without compacting it. Pass
        *minimum_weight* ``0`` to select all entries.
        :raises: :exc:`IndexError` if no entries are found. Use
            :func:`~chess.polyglot.MemoryMappedReader.get()` if you prefer to
            get ``None`` instead of an exception.
        """
        try:
            return max(self.find_all(game, minimum_weight=minimum_weight), key=lambda entry: entry.weight)
        except ValueError:
            raise IndexError()

    def get(self, game, default: Optional[Entry] = None, *, minimum_weight: int = 1) -> Optional[Entry]:
        try:
            return self.find(game, minimum_weight=minimum_weight)
        except IndexError:
            return default

    def choice(self, game, *, minimum_weight: int = 1, random: Optional[random.Random] = None) -> Entry:
        """
        Uniformly selects a random entry for the given position.
        :raises: :exc:`IndexError` if no entries are found.
        """
        chosen_entry = None

        for i, entry in enumerate(self.find_all(game, minimum_weight=minimum_weight)):
            if chosen_entry is None or _randint(random, 0, i) == i:
                chosen_entry = entry

        if chosen_entry is None:
            raise IndexError()

        return chosen_entry

    def weighted_choice(self, game, *, random: Optional[random.Random] = None) -> Entry:
        """
        Selects a random entry for the given position, distributed by the
        weights of the entries.
        :raises: :exc:`IndexError` if no entries are found.
        """
        total_weights = sum(entry.weight for entry in self.find_all(game))
        if not total_weights:
            raise IndexError()

        choice = _randint(random, 0, total_weights - 1)

        current_sum = 0
        for entry in self.find_all(game):
            current_sum += entry.weight
            if current_sum > choice:
                return entry

        assert False

    def close(self) -> None:
        """Closes the reader."""
        self.mmap.close()

        try:
            os.close(self.fd)
        except OSError:
            pass


def open_reader(path: PathLike) -> MemoryMappedReader:
    return MemoryMappedReader(path)
