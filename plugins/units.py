#!/usr/bin/env python
import sys, json, re, os, subprocess

def query(q):
    if not os.path.exists("/usr/bin/units"):
        print json.dumps({"results": []})
        return
    m = re.match(r"^\s*([0-9.]+)\s*([A-Za-z]+)\s+in\s+([A-Za-z]+)\s*$", q)
    if m:
        fromunit = m.groups()[1]
        tounit = m.groups()[2]
        cmd = ["units", "-v", "-1", "%s %s" % (float(m.groups()[0]), fromunit), tounit]
        try:
            out = subprocess.check_output(cmd).strip()
            if "Unknown" in out:
                print json.dumps({"results": []})
                return
            print json.dumps({"results": [{"name": out, "key": out, "score": 100,
                "icon": "/usr/share/icons/Humanity/apps/48/gnome-session-switch.svg",
                "description": ""}]})
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
