from collections import defaultdict
from xml.dom import minidom
from fa import FA

def get_source_node(t):
    return t.getElementsByTagName('from')[0].firstChild.nodeValue

def get_target_node(t):
    return t.getElementsByTagName('to')[0].firstChild.nodeValue

def get_read_symbol(t):
    n = t.getElementsByTagName('read')[0].firstChild
    return n.nodeValue if n else n

def read_transition(t):
    return ((get_source_node(t), get_read_symbol(t)), get_target_node(t))

def build_transitions(xmldoc):
    """ return a defaultdict(list) for the transitions, both for a
    dfa and nfa
    """
    transitionlist = xmldoc.getElementsByTagName('transition')
    transitions = defaultdict(list)
    for k,v in map(read_transition, transitionlist):
        transitions[k].append(v)
    return transitions

def is_epsilon(transition):
    if not state.getElementsByTagName('read'):
        return False
    return True

def is_initial(state):
    if not state.getElementsByTagName('initial'):
        return False
    return True

def is_final(state):
    if not state.getElementsByTagName('final'):
        return False
    return True

def get_states(xmldoc):
    # returns a triple: states, start, ends (Q, q0, F)
    state_list = xmldoc.getElementsByTagName('state')
    states = set()
    q0 = None
    final_states = set()
    for s in state_list:
        if is_initial(s):
            q0 = s.attributes['id'].value
        if is_final(s):
            final_states.add(s.attributes['id'].value)
        states.add(s.attributes['id'].value)
    return (states, q0, final_states)


def fa_from_jflapxml(xmldoc):
    transitions = build_transitions(xmldoc)
    alphabet = set(c for (_,c) in transitions.keys())
    states, q0, final_states = get_states(xmldoc)
    fa_type = 'DFA'
    for (state,symbol),t in transitions.items():
        if (len(t) > 1) or symbol is None:
            fa_type = 'NFA'
            break
    return FA(states, alphabet, transitions, q0, final_states, fa_type)
