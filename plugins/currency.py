#!/usr/bin/env python
import sys, json, re, urllib, decimal
from xml.dom import minidom

def query(q):
    m = re.match(r"^\s*([0-9]+)\s*([A-Za-z][A-Za-z][A-Za-z])\s+in\s+([A-Za-z][A-Za-z][A-Za-z])\s*$", q)
    if m:
        base = m.groups()[1].upper()
        target = m.groups()[2].upper()
        url = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
        try:
            fp = urllib.urlopen(url)
            data = fp.read()
            fp.close()
            dom = minidom.parseString(data)
            curs = dict([(x.getAttribute("currency"), decimal.Decimal(x.getAttribute("rate")))
                for x in dom.getElementsByTagName("Cube")[0].getElementsByTagName("Cube")[0].getElementsByTagName("Cube")])
            base_value = decimal.Decimal(m.groups()[0])
            if base == "EUR":
                base_eur = base_value
            else:
                base_eur = base_value / curs[base]
            if target == "EUR":
                target_value = base_eur
            else:
                target_value = base_eur * curs[target]
            res = "{:.2f}{}".format(target_value, target)
            print json.dumps({"results": [{
                "name": res,
                "key": res, "score": 100,
                "icon": "/usr/share/icons/Humanity/emblems/48/emblem-money.svg",
                "description": "currency conversion from ecb.europa.eu"}]})
        except Exception as e:
            print json.dumps({"results": []})
    else:
        print json.dumps({"results": []})

def invoke(key):
    pass # not really a lot we can do here.

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print >> sys.stderr, "Bad invocation %r" % (sys.argv,)
    elif sys.argv[1] == "--query":
        query(sys.argv[2])
    elif sys.argv[1] == "--invoke":
        invoke(sys.argv[2])
    else:
        print >> sys.stderr, "Bad command %s" % (sys.argv[1],)
