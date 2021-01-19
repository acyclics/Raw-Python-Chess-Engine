import numpy as np

from engine.zobrist_hashing import ZobristHashing


class Transposition():

    def __init__(self, size):
        self.size = size
        self.hashtable = [None for _ in range(size)]

    def hash_function(self, key):
        return key % self.size

    def replace(self, entry1, entry2):
        # Keep the deepest search
        if entry1['depth'] > entry2['depth']:
            return entry1
        else:
            return entry2

    def add_entry(self, key, depth, evaluation, best_move):
        entry = {
            'key': key,
            'depth': depth,
            'evaluation': evaluation,
            'best_move': best_move
        }
        hash_key = self.hash_function(key)

        if self.hashtable[hash_key] != None:
            self.hashtable[hash_key] = self.replace(self.hashtable[hash_key], entry)
        else:
            self.hashtable[hash_key] = entry
    
    def lookup(self, key):
        entry = self.hashtable[self.hash_function(key)]
        if entry != None and entry['key'] == key:
            return entry
        else:
            return None
