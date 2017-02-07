from dfa import dfa_run

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
        return run_as_dfa(fa, input)
    else:
        return "NFA not yet working"
