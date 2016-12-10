from collections import namedtuple, defaultdict
import random
import itertools
from dfa import DFA

NFA = namedtuple('NFA', ['Q', 'Sigma', 'delta', 'q0', 'F'])


def nfa_gen_seq(nfa, transitions=None, min_len=0, max_len=50):
    # min,max not implemented
    if not transitions:
        transitions = defaultdict(list)
        for (state, symbol), new_states in nfa.delta.items():
            transitions[state].append((new_states, symbol))
    state = random.choice(list(nfa.q0))
    seq   = []
    lo    = min_len
    hi    = max_len
    while state not in nfa.F:
        (states, symbol) = random.choice(transitions[state])
        state = random.choice(list(states))
        if symbol != 'epsilon':
            seq.append(symbol)
    return ''.join(reversed(seq))

def nfa_gen_seqs(nfa):
    transitions = defaultdict(list)
    for (state, symbol), new_states in nfa.delta.items():
        transitions[state].append((new_states, symbol))
    while True:
        yield nfa_gen_seq(nfa, transitions)




def test():
    nfa1 = NFA({1,2,3},
           {'a','b'},
           {# (1,'epsilon') : {3},
            (1,'b') : {2},
            (2,'b') : {3},
            (2,'a') : {2,3},
            (3, 'epsilon') : {2},
            (2, 'epsilon') : {1},
            (3,'a') : {1}},
           {1},
           {3})

    return list(sorted(set(itertools.islice(nfa_gen_seqs(nfa1), 100))))



def powerset_generator(s):
    # O(2 ^ len(s))
    for i in xrange(len(s)+1):
        for j in itertools.combinations(s, i):
            yield frozenset(j)




def nfa_to_dfa(nfa):
    """
    converts a NFA into a DFA
    """

    dfa_Sigma = nfa.Sigma.copy()
    dfa_Q     = set(powerset_generator(nfa.Q))
    dfa_q0    = nfa.q0.copy()
    dfa_q0   |= epsilon_closure(nfa, nfa.Q)
    dfa_delta = dict()
    dfa_F     = set()

    print 'all states for new DFA :', dfa_Q
    print 'start state for new DFA :', dfa_q0

    # calculate end states, all sets S in dfa_Q such that S intersect nfa.F
    # is not empty

    for stateSet in dfa_Q:
        # print stateSet, nfa.F
        if len(stateSet.intersection(nfa.F)) > 0:
            dfa_F.add(stateSet)

    print 'accept states for new DFA :', dfa_F


    # find 'free' transitions. Given a state S, which {states} can we
    # move to using only epsilon transitions
    epsilons = defaultdict(set)
    for (state,symbol), moves in nfa.delta.items():
        if symbol == 'epsilon':
            epsilons[state] = moves

    # if we worked backwards we could just add the paths (sets)

    epsilon_starts = epsilons.keys()
    while epsilon_starts:
        e = epsilon_starts.pop()
        stack = [e]
        seen = set()
        reachable = set()
        while stack:
            state = stack.pop()
            if state not in seen:
                seen.add(state)
                reachable |= epsilons[state]
                stack.extend(epsilons[state])
        epsilons[e] = reachable

    # union the moves
    d = {}
    for (state, symbol), moves in nfa.delta.items():
        d[(state, symbol)] = moves
        s = set()
        if symbol != 'epsilon':
            for move in moves:
                s.add(move)
                s |= epsilons.get(move, set())
            d[(state, symbol)] |= s

    print 'initial moves calculated :', d



def epsilon_closure(nfa, state_set):
    """
    given a set of states, find the epsilon closure
    """
    stack_set = state_set.copy()
    closure = set()
    while stack_set:
        moves = nfa.delta.get((stack_set.pop(), 'epsilon'), set())
        for m in moves:
            if m not in closure:
                closure.add(m)
                stack_set.add(m)
    return closure
