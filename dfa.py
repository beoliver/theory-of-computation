from collections import namedtuple, defaultdict
import random
from itertools import islice
from fa_types import DFA

# a dfa is a 5-tuple
# (Q, sigma, delta, q0, F) where
# Q is a finite set of states
# sigma is a finite set called the alphabet
# delta : Q x sigma -> Q (transition function)
# q0 is the start state (an element in Q)
# F is a set of accept states (F \subseteq Q)

def dfa_run(dfa, seq):
    state = dfa.q0
    for s in seq:
        state = dfa.delta.get((state, s), None)
        if not state:
            return False
    return state in dfa.F

# a DFA can also be used to generate strings from
# the language that it describes
#

def dfa_remove_explicit_sink_states(dfa):
    """
    removes all paths that do not lead from q0 to F
    idempotent, (each call returns a new dfa)
    """
    # create an alternative graph, state : {prev_state1, ..., prev_stateN}
    graph_prev = defaultdict(set)
    for (state, symbol), new_state in dfa.delta.items():
        graph_prev[new_state].add(state)

    # as the dfa has a start and (multiple) ends,
    # we can start at the end and work backwards.
    # if a state p points to an element in F, but p is not
    # reachable when starting at q0 then we ignore it

    stack = list(dfa.F)
    valid = set() # valid visited states
    while stack:
        state = stack.pop()
        if state not in valid:
            previous = graph_prev.get(state, set())
            if previous or state == dfa.q0:
                valid.add(state)
                stack.extend(previous)
    alphabet = set()
    delta = {}
    for (state, symbol), new_state in dfa.delta.items():
        if state in valid and new_state in valid:
            alphabet.add(symbol)
            delta[(state, symbol)] = new_state
    return DFA(valid, alphabet, delta, dfa.q0, dfa.F)


def dfa_gen_seq(dfa, transitions=None):
    if not transitions:
        transitions = defaultdict(list)
        for (state, symbol), new_state in dfa.delta.items():
            transitions[state].append((new_state, symbol))
    state = dfa.q0
    seq   = []
    while state not in dfa.F:
        (state, symbol) = random.choice(transitions[state])
        seq.append(symbol)
    return ''.join(reversed(seq))

def dfa_gen_seqs(dfa):
    dfa = dfa_remove_explicit_sink_states(dfa)
    transitions = defaultdict(list)
    for (state, symbol), new_state in dfa.delta.items():
        transitions[state].append((new_state, symbol))
    while True:
        yield dfa_gen_seq(dfa, transitions)


dfa1 = DFA({0, 1, 2}, {'a','b'}, {(0,'a'):1, (0,'b'):2, (1,'a'):2}, 0, {2})

# in dfa2 states 5 and 6 represent explicit 'sink' states
dfa2 = DFA({0, 1, 2, 3, 4, 5, 6, 7},
           {'a','b','c','d'},
           {
               (0,'a'):4,
               (0,'b'):2,
               (0,'c'):1,
               (0,'d'):5,
               (1,'a'):2,
               (1,'b'):3,
               (1,'c'):6,
               (2,'a'):4,
               (2,'b'):0,
               (4,'b'):3,
               (5,'d'):7
           },
           0, {3})


def test():
    for s in sorted(set(islice(dfa_gen_seqs(dfa2), 1000))):
        print s
