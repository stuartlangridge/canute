#!/usr/bin/env python
import sys, json, re, urllib

def query(q):
    m = re.match(r"^\s*([0-9]+)\s*([A-Za-z][A-Za-z][A-Za-z])\s+in\s+([A-Za-z][A-Za-z][A-Za-z])\s*$", q)
    if m:
        base = m.groups()[1].upper()
        symbols = m.groups()[2].upper()
        url = "http://api.fixer.io/latest?base=%s&symbols=%s" % (base, symbols)
        try:
            fp = urllib.urlopen(url)
            data = fp.read()
            d = json.loads(data)
            r = d["rates"][symbols]
            res = float(m.groups()[0]) * r
            print json.dumps({"results": [{"name": "%s%s" % (res, symbols), "key": "%s%s" % (res, symbols), "score": 100,
                "icon": "/usr/share/icons/Humanity/emblems/48/emblem-money.svg",
                "description": "currency conversion from fixer.io"}]})
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
