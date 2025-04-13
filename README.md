Regex to NFA Converter

A Python implementation of Thompson's Construction that converts regular expressions into Non-deterministic Finite Automata (NFAs).
Features

Supports regex operators:

    * (Kleene Star)

    + (Kleene Plus)

    ? (Option)

    | (Union)

    . (Concatenation, auto-inserted)

    ( ) (Grouping)

Converts infix regex to postfix notation using the Shunting Yard algorithm.
Builds an NFA with epsilon (ε) transitions.

