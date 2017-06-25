from collections import namedtuple, defaultdict
import random
from itertools import islice
from fa_types import DFA
import copy

# regular languages are closed under
# union,
# intersection,
# concatenation,
# kleene star
# difference
# complementation
# reversal


# a dfa is a 5-tuple
# (Q, sigma, delta, q0, F) where
# Q is a finite set of states
# sigma is a finite set called the alphabet
# delta : Q x sigma -> Q (transition function)
# q0 is the start state (an element in Q)
# F is a set of accept states (F \subseteq Q)

def no_symbol_transition_map(dfa):
    d = defaultdict(set)
    for ((k,s),v) in dfa.delta.items():
        d[k].add(v)
    return d


def reachable_states(dfa):
    """returns a set of states that can be reached from the start state"""
    state = dfa.q0
    visited = set([state])
    transitions = no_symbol_transition_map(dfa)
    unvisited = transitions[state].copy()
    while unvisited:
        move_state = unvisited.pop()
        if move_state in visited:
            continue
        else:
            visited.add(move_state)
            unvisited |= transitions[move_state]
    return visited

def unreachable_states(dfa):
    """returns a set of states that can not be reached from the start state"""
    return dfa.Q.difference(reachable_states(dfa))

def hopcrofts_algorithm(dfa, unreachable_states):
    u = unreachable_states
    f = frozenset(dfa.F.difference(u))
    p = [f, frozenset(dfa.Q.difference(f).difference(u))] # a list not a set
    w = set([f])
    d = dfa.delta.items()
    while w:
        a = w.pop()
        x = set([])
        # new_d = []
        iteration = 0
        for c in dfa.Sigma:
            for ((state,symbol),move) in d:
                if (symbol == c) and (move in a):
                    x.add(state)
                # else:
                #     new_d.append(((state,symbol),move))
            index = 0
            while index < len(p):
                y = p[index]
                xy_inter = frozenset(x.intersection(y))
                yx_diff = frozenset(y.difference(x))
                if xy_inter and yx_diff:
                    p.pop(index)
                    p.append(xy_inter)
                    p.append(yx_diff)
                    if y in w:
                        w -= y
                        w.add(xy_inter)
                        w.add(yx_diff)
                    else:
                        if len(xy_inter) <= len(yx_diff):
                            w.add(xy_inter)
                        else:
                            e.add(yx_diff)
                else:
                    index += 1
            # d = new_d
    return p

def minimize(dfa):
    u = unreachable_states(dfa)
    partitions = hopcrofts_algorithm(dfa, u)
    if len(partitions) == len(dfa.Q):
        return dfa
    else:
        # create a set of new states... there are exactly len(partitions) states
        # map the old states to the new states (many to one)
        m = {}
        for new_state,partition in enumerate(partitions):
            for p in partition:
                m[p] = new_state
        # create a new delta (transition) mapping
        new_delta = {}
        for ((state, symbol), new_state) in dfa.delta.items():
            if state in u or new_state in u:
                continue
            new_delta[(m[state], symbol)] = m[new_state]
        new_accept = set(m[x] for x in dfa.F if x not in u)
        return DFA(set(range(len(partitions))),dfa.Sigma,new_delta,m[dfa.q0],new_accept)


def run(dfa, seq, verbose=False):
    """Given a DFA D and an input sequence s, run s on D.
    returns True If D accepts s else False
    """
    state = dfa.q0
    for s in seq:
        if verbose:
            print ("state=%s, reading symbol=%s" % (state, s))
        state = dfa.delta.get((state, s), None)
        if state == None:
            return False
    return state in dfa.F

def complement(dfa):
    return dfa._replace(F = dfa.Q.difference(dfa.F))

def cross_product(a,b):
    for x in a:
        for y in b:
            yield (x,y)

def product(dfa1, dfa2, pred=lambda x,y : (x,y) != (None,None)):
    """does not compute the accept states F"""
    Q = set(cross_product(dfa1.Q, dfa2.Q)) # states
    Sigma = dfa1.Sigma.union(dfa2.Sigma)
    q0 = (dfa1.q0, dfa2.q0) # start state
    delta = dict()
    for (x,y) in Q:
        for s in Sigma:
            updated = (a,b) = (dfa1.delta.get((x,s),None), dfa2.delta.get((y,s),None))
            if pred(*updated):
                delta[((x,y),s)] = updated
    return DFA(Q,Sigma,delta,q0,set())

# def concat(dfa1, dfa2):
#     """return a new dfa that recognizes L1L2"""
#     # states must be renamed to be unique
#     state_index = 0
#     state_rename_map1 = {}
#     for state in dfa1.Q:
#         state_rename_map1[state] = state_index
#         state_index += 1
#     state_rename_map1 = {}
#     for state in dfa2.Q:
#         state_rename_map2[state] = state_index
#         state_index += 1
#     F = dfa2.F
#     Q = set(range(state_index))
#     Sigma = dfa1.Sigma.union(dfa2.Sigma)
#     q0 = dfa1.q0
#     delta = {}
#     for (current_state, symbol),new_state in dfa2.delta.items():
#         delta[(state_rename_map2[current_state], symbol)] = state_rename_map2[new_state]
#     for (current_state, symbol),new_state in dfa1.delta.items():
#         delta[(state_rename_map2[current_state], symbol)] = state_rename_map2[new_state]
#         if current_state in dfa1.F:
#             delta[(state_rename_map2[current_state], symbol)]





def intersection(dfa1, dfa2):
    dfa3 = product(dfa1, dfa2, lambda x,y : (x != None) and (y != None))
    return dfa3._replace(F = set(cross_product(dfa1.F, dfa2.F)))

def union(dfa1, dfa2):
    dfa3 = product(dfa1, dfa2)
    return dfa3._replace(F = set((x,y) for (x,y) in dfa3.Q if x in dfa1.F or y in dfa2.F))

def difference(dfa1, dfa2):
    return dfa3._replace(F = set((x,y) for (x,y) in dfa3.Q if x in dfa1.F and y not in dfa2.F))

def equivalent(dfa1, dfa2, verbose=False):
    """not working as expected..."""
    p = product(dfa1, dfa2)
    accept1 = dfa1.F
    accept2 = dfa2.F
    a_eq_b = 0
    a_gt_b = 0
    a_lt_b = 0
    unrelated = 0
    for (x,y) in [(x,y) for (x,y) in p.Q if x in accept1 or y in accept2]:
        print((x,y))
        a = x in accept1
        b = y in accept2
        if a and b:
            a_eq_b += 1
        elif a:
            a_gt_b += 1
        elif b:
            a_lt_b += 1
        else:
            unrelated += 1
        if verbose:
            print ("a_eq_b : %d, a_lt_b : %d, a_gt_b : %d, a_ne_b : %d" % (a_eq_b, a_lt_b, a_gt_b, unrelated))
    assert a_eq_b + a_gt_b + a_lt_b + unrelated > 0
    if a_gt_b + a_lt_b + unrelated == 0:
        return 0
    if a_eq_b + a_lt_b + unrelated == 0:
        return 1
    if a_eq_b + a_gt_b + unrelated == 0:
        return -1
    return "unrelated" # not related at all

# a DFA can also be used to generate strings from
# the language that it describes

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


# dfa1 = DFA({0, 1, 2}, {'a','b'}, {(0,'a'):1, (0,'b'):2, (1,'a'):2}, 0, {2})

# in dfa2 states 5 and 6 represent explicit 'sink' states
# dfa2 = DFA({0, 1, 2, 3, 4, 5, 6, 7},
#            {'a','b','c','d'},
#            {
#                (0,'a'):4,
#                (0,'b'):2,
#                (0,'c'):1,
#                (0,'d'):5,
#                (1,'a'):2,
#                (1,'b'):3,
#                (1,'c'):6,
#                (2,'a'):4,
#                (2,'b'):0,
#                (4,'b'):3,
#                (5,'d'):7
#            },
#            0, {3})


# def test():
#     for s in sorted(set(islice(dfa_gen_seqs(dfa2), 1000))):
#         print s
