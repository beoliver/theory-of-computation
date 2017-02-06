import sys
from xml.dom import minidom
from jflap_dfa_reader import dfa_from_jflapxml
from dfa import dfa_run

if __name__ == '__main__':
    f = sys.argv[1]
    xmldoc = minidom.parse(f)
    dfa = dfa_from_jflapxml(xmldoc)
    test_input = sys.argv[2]
    print dfa_run(dfa, test_input)
