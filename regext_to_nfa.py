"""
regex_to_nfa.py

A Python implementation that converts a regular expression (in a simplified form)
into a Non-deterministic Finite Automaton (NFA) using Thompson's Construction.

Supported Operators:
  - '*' (Star: zero or more repetitions)
  - '+' (Plus: one or more repetitions)
  - '?' (Option: zero or one occurrence)
  - '|' (Union / Alternation)
  - '.' (Concatenation, inserted internally)
  - '(' and ')' (Grouping)

"""


class NFA:
    """
    Represents a Non-deterministic Finite Automaton (NFA).

    Attributes:
        start_state (int): The integer ID of the start state.
        accept_state (int): The integer ID of the accept (final) state.
        transitions (dict): A nested dictionary describing state transitions,
                            of the form transitions[state][symbol] = set_of_next_states,
                            where 'symbol' can be a literal character (e.g., 'a')
                            or the special symbol 'ε' for an epsilon transition.
    """

    def __init__(self, start_state, accept_state, transitions=None):
        """
        Initialize the NFA.

        Args:
            start_state (int): The start state ID.
            accept_state (int): The accept (final) state ID.
            transitions (dict, optional): Transition table. Defaults to None.
        """
        self.start_state = start_state
        self.accept_state = accept_state
        self.transitions = transitions if transitions is not None else {}

    def add_transition(self, from_state, symbol, to_state):
        """
        Add a transition to the NFA's transition dictionary.

        Args:
            from_state (int): ID of the current state.
            symbol (str): Transition symbol (e.g., 'a' or 'ε').
            to_state (int): ID of the next state.
        """
        if from_state not in self.transitions:
            self.transitions[from_state] = {}
        if symbol not in self.transitions[from_state]:
            self.transitions[from_state][symbol] = set()
        self.transitions[from_state][symbol].add(to_state)


def infix_to_postfix(regex):
    """
    Convert a regular expression in infix notation to postfix notation,
    using an approach similar to the Shunting Yard algorithm.

    We first insert an explicit concatenation operator '.' where needed,
    then apply operator-precedence rules to generate the final postfix.

    Operator Precedence (highest to lowest):
      1) Kleene star (*), plus (+), and question mark (?)
      2) Concatenation (.)
      3) Union (|)

    Args:
        regex (str): The infix regular expression (e.g., "(a|b)?a")

    Returns:
        str: The postfix regex string.
    """

    # Step 1: Insert '.' for concatenation where implied
    explicit = []
    length = len(regex)

    for i in range(length):
        c = regex[i]
        explicit.append(c)

        if i < length - 1:
            nxt = regex[i + 1]
            # We insert '.' if:
            #  - c is not in ['(', '|'] (means c is either a literal, ')', or an operator like '*','+','?')
            #  - nxt is not in [')', '|', '*', '+', '?'] (means nxt is a literal or '(')
            if ((c not in ['(', '|']) and
                    (nxt not in [')', '|', '*', '+', '?'])):
                explicit.append('.')

    # Convert list back to string
    regex = "".join(explicit)

    # Step 2: Convert to postfix (Shunting Yard method)
    output = []
    stack = []

    # Define operator precedence
    precedence = {
        '*': 3,
        '+': 3,
        '?': 3,
        '.': 2,
        '|': 1,
        '(': 0  # '(' has lowest precedence when on the stack
    }

    for char in regex:
        if char == '(':
            stack.append(char)
        elif char == ')':
            # Pop from stack until '(' is found
            top = stack.pop()
            while top != '(':
                output.append(top)
                top = stack.pop()
        elif char in ['*', '+', '?', '.', '|']:
            # While there's an operator at the top of the stack
            # with higher or equal precedence, pop it
            while stack and precedence[stack[-1]] >= precedence[char]:
                output.append(stack.pop())
            stack.append(char)
        else:
            # Operand (assume single character literal)
            output.append(char)

    # Pop any remaining operators
    while stack:
        output.append(stack.pop())

    return "".join(output)


def postfix_to_nfa(postfix):
    """
    Convert a postfix regular expression into an NFA using Thompson's Construction.

    Rules:
      - For a literal 'a', create an NFA with one transition from start to accept on 'a'.
      - For 'E *', Kleene star (zero or more).
      - For 'E +', Kleene plus (one or more).
      - For 'E ?', Option (zero or one).
      - For 'E1 E2 .', Concatenation.
      - For 'E1 E2 |', Union.

    Args:
        postfix (str): The postfix regular expression.

    Returns:
        NFA: The resulting NFA.
    """

    # A helper to generate new unique state IDs
    next_state_id = [0]

    def new_state():
        s = next_state_id[0]
        next_state_id[0] += 1
        return s

    stack = []

    for char in postfix:
        if char not in ['*', '+', '?', '.', '|']:
            # Single-character literal
            start = new_state()
            accept = new_state()
            nfa = NFA(start, accept)
            nfa.add_transition(start, char, accept)
            stack.append(nfa)

        elif char == '*':
            # Kleene Star: zero or more
            nfa1 = stack.pop()
            start = new_state()
            accept = new_state()

            # Create a new NFA that includes nfa1
            nfa = NFA(start, accept, dict(nfa1.transitions))

            # Epsilon transitions for *
            # (1) new_start -> nfa1.start_state
            nfa.add_transition(start, 'ε', nfa1.start_state)
            # (2) nfa1.accept_state -> nfa1.start_state
            nfa.add_transition(nfa1.accept_state, 'ε', nfa1.start_state)
            # (3) new_start -> new_accept
            nfa.add_transition(start, 'ε', accept)
            # (4) nfa1.accept_state -> new_accept
            nfa.add_transition(nfa1.accept_state, 'ε', accept)

            stack.append(nfa)

        elif char == '+':
            # Kleene Plus: one or more
            nfa1 = stack.pop()
            start = new_state()
            accept = new_state()

            # Create a new NFA that includes nfa1
            nfa = NFA(start, accept, dict(nfa1.transitions))

            # Epsilon transitions for +
            # Must go through nfa1 at least once:
            # (1) new_start -> nfa1.start_state
            nfa.add_transition(start, 'ε', nfa1.start_state)
            # (2) nfa1.accept_state -> nfa1.start_state
            nfa.add_transition(nfa1.accept_state, 'ε', nfa1.start_state)
            # (3) nfa1.accept_state -> new_accept
            nfa.add_transition(nfa1.accept_state, 'ε', accept)

            stack.append(nfa)

        elif char == '?':
            # Option: zero or one occurrence
            nfa1 = stack.pop()
            start = new_state()
            accept = new_state()

            # Create a new NFA that includes nfa1
            nfa = NFA(start, accept, dict(nfa1.transitions))

            # Epsilon transitions for ?
            # (1) new_start -> nfa1.start_state (the "one" part)
            nfa.add_transition(start, 'ε', nfa1.start_state)
            # (2) nfa1.accept_state -> new_accept
            nfa.add_transition(nfa1.accept_state, 'ε', accept)
            # (3) new_start -> new_accept (the "zero" part)
            nfa.add_transition(start, 'ε', accept)

            stack.append(nfa)

        elif char == '.':
            # Concatenation: pop 2 NFAs
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            nfa = NFA(nfa1.start_state, nfa2.accept_state, dict(nfa1.transitions))

            # Merge nfa2's transitions into nfa
            for state in nfa2.transitions:
                for symbol, destinations in nfa2.transitions[state].items():
                    if state not in nfa.transitions:
                        nfa.transitions[state] = {}
                    if symbol not in nfa.transitions[state]:
                        nfa.transitions[state][symbol] = set()
                    nfa.transitions[state][symbol].update(destinations)

            # Epsilon transition from nfa1.accept_state to nfa2.start_state
            nfa.add_transition(nfa1.accept_state, 'ε', nfa2.start_state)

            stack.append(nfa)

        elif char == '|':
            # Union: pop 2 NFAs
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            start = new_state()
            accept = new_state()

            nfa = NFA(start, accept, dict(nfa1.transitions))

            # Merge transitions from nfa2
            for state in nfa2.transitions:
                for symbol, destinations in nfa2.transitions[state].items():
                    if state not in nfa.transitions:
                        nfa.transitions[state] = {}
                    if symbol not in nfa.transitions[state]:
                        nfa.transitions[state][symbol] = set()
                    nfa.transitions[state][symbol].update(destinations)

            # Epsilon transitions for union
            nfa.add_transition(start, 'ε', nfa1.start_state)
            nfa.add_transition(start, 'ε', nfa2.start_state)
            nfa.add_transition(nfa1.accept_state, 'ε', accept)
            nfa.add_transition(nfa2.accept_state, 'ε', accept)

            stack.append(nfa)

        else:
            raise ValueError(f"Unexpected symbol '{char}' in postfix expression.")

    # There should be exactly one NFA on the stack
    if len(stack) != 1:
        raise ValueError("Invalid postfix expression: stack does not contain exactly one NFA at the end.")

    return stack.pop()


def regex_to_nfa(regex):
    """
    Converts an infix regular expression to an NFA by:
      1) Converting infix to postfix (with explicit '.' for concatenation),
      2) Using Thompson's construction on the postfix form.

    Args:
        regex (str): A simplified regular expression (e.g., "(a|b)?a").

    Returns:
        NFA: A Non-deterministic Finite Automaton that recognizes the same language.
    """
    postfix = infix_to_postfix(regex)
    return postfix_to_nfa(postfix)


if __name__ == "__main__":
    # Example usage:
    example_regex = "(a|b)?a"
    nfa = regex_to_nfa(example_regex)

    print("Regular Expression:", example_regex)
    print("Postfix:", infix_to_postfix(example_regex))
    print("Start State:", nfa.start_state)
    print("Accept State:", nfa.accept_state)
    print("Transitions:")
    for s in sorted(nfa.transitions.keys()):
        for sym, destinations in nfa.transitions[s].items():
            print(f"  {s} --{sym}--> {sorted(destinations)}")
