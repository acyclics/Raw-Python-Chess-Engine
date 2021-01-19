# Raw Python Chess Engine
This repository contains a simple chess-engine I written in Python for a course. To summarize, my method is to first formulate a state-space for searching through game-states with alpha-beta pruning, to improve upon alpha-beta pruning via techniques such as quiescence search, to reduce the amount of computation needed via hashing, and to engineer in domain knowledge through opening tables and piece heuristics. Specifically, I have implemented the following:

Chess state-space formulation
Alpha-beta pruning
Quiescence search
Transposition table
Iterative deepening
Aspiration window
Opening book
Chess-based heuristics
MVV-LVA move-ordering

Details of each implementation and methods can be found in the report contained within this repository.
