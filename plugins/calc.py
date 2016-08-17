#!/usr/bin/env python
import sys, json, re

try:
    from sympy import *
    x, y, z = symbols("x y z")
except:
    symbols = None

def query(q):
    if not symbols:
        if re.match(r"^[0-9\+\-\/\* \(\)]+$"):
            print json.dumps({"results": [{"name": "Calculator", "key": "NOCALC", "score": 60,
                "icon": "/usr/share/icons/Humanity/apps/22/accessories-calculator.svg",
                "description": "Install python-sympy to make the calculator work"}]})
            return
    try:
        expr = sympify(q)
    except:
        print json.dumps({"results": []})
        return
    if str(expr) == q:
        print json.dumps({"results": []})
        return
    print json.dumps({"results": [{"name": str(expr), "key": str(expr), "score": 60,
        "icon": "/usr/share/icons/Humanity/apps/22/accessories-calculator.svg",
        "description": None}]})

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
