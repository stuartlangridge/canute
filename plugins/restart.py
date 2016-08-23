#!/usr/bin/env python
import sys, json, re

try:
    from sympy import *
    x, y, z = symbols("x y z")
except:
    symbols = None

def query(q):
    if q == "restart":
        print json.dumps({
            "results": [
                {
                    "name": "Restart Canute",
                    "key": "special_restart",
                    "score": 100,
                    "icon": None,
                    "description": "Restart this application launcher"
                }
            ]
        })
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
