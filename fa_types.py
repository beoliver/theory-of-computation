from collections import namedtuple

DFA = namedtuple('DFA', ['Q', 'Sigma', 'delta', 'q0', 'F'])
NFA = namedtuple('NFA', ['Q', 'Sigma', 'delta', 'q0', 'F'])
FA  = namedtuple('FA', ['Q', 'Sigma', 'delta', 'q0', 'F', 'type'])
