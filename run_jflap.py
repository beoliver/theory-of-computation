import sys
from xml.dom import minidom
from jflap_fa_reader import fa_from_jflapxml
from fa import run

if __name__ == '__main__':
    f = sys.argv[1]
    xmldoc = minidom.parse(f)
    fa = fa_from_jflapxml(xmldoc)
    t = sys.argv[2]
    if t.upper() != fa.type:
        print f + " is not of type " + t
        sys.exit()
    test = sys.argv[3]
    print run(fa, test)
