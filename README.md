# Raw Python Chess Engine
This repository contains a simple chess-engine I written in Python for a course. To summarize, my method is to first formulate a state-space for searching through game-states with alpha-beta pruning, to improve upon alpha-beta pruning via techniques such as quiescence search, to reduce the amount of computation needed via hashing, and to engineer in domain knowledge through opening tables and piece heuristics. Specifically, I have implemented the following:

1. Chess state-space formulation

2. Alpha-beta pruning

3. Quiescence search

4. Transposition table

5. Iterative deepening

6. Aspiration window

7. Opening book

8. Chess-based heuristics

9. MVV-LVA move-ordering

Details of each implementation and methods can be found in the report contained within this repository.
