#!/usr/bin/env python
import sys, json
from subprocess import Popen, PIPE, STDOUT

EMOJI = {"nope": "1f600"}

def query(q):
    is_shortcode = False
    if q.startswith(":"):
        is_shortcode = True
        q = q[1:]
    matches = [x for x in EMOJI.keys() if x.startswith(q.lower().replace(" ", "_"))]
    if not matches:
        print json.dumps({"results": []})
        return
    results = [
        {"name": unichr(int(EMOJI[x], 16)), "key": x, "score": 100 if is_shortcode else 100 * len(q) / len(x),
        "icon": "/usr/share/icons/gnome/scalable/apps/accessories-character-map-symbolic.svg", "description": ":%s:" % x}
        for x in matches
    ]
    print json.dumps({"results": results})


def invoke(key):
    char = unichr(int(EMOJI[key], 16)).encode("utf-8")
    p = Popen(["xclip", "-i", "-selection", "clipboard"], stdin=PIPE)
    res = p.communicate(input=char)
    p.stdin.close()
    p = Popen(["xclip", "-i", "-selection", "primary"], stdin=PIPE)
    res = p.communicate(input=char)
    p.stdin.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print >> sys.stderr, "Bad invocation %r" % (sys.argv,)
    elif sys.argv[1] == "--query":
        query(sys.argv[2])
    elif sys.argv[1] == "--invoke":
        invoke(sys.argv[2])
    else:
        print >> sys.stderr, "Bad command %s" % (sys.argv[1],)
