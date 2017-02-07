from collections import namedtuple
from dfa import dfa_run

FA = namedtuple('FA', ['Q', 'Sigma', 'delta', 'q0', 'F', 'type'])

def run_as_dfa(fa, seq):
    state = fa.q0
    for s in seq:
        state = fa.delta.get((state, s), [])
        if not state:
            return False
        else:
            state = state[0]
    return state in fa.F


def run(fa, input):
    if fa.type is 'DFA':
        print run_as_dfa(fa, input)
    else:
        print "NFA not yet working"
