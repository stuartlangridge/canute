#!/usr/bin/env python
import sys, json, subprocess, re

ansi_escape = re.compile(r'\x1b[^m]*m')

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk

def query(q):
    out = subprocess.check_output(["pass", "find", q])
    out = ansi_escape.sub('', out)
    out = out.decode("utf8")
    out = out.replace(u"\u2514", " ").replace(u"\u251c", " ").replace(u"\u2502", " ").replace(u"\u2500", " ")
    indent_length = None
    current_indents = 0
    prefixes = []
    passes = []
    for line in out.split("\n")[1:]: # skip first line, which shows "Search terms"
        ls = line.lstrip()
        line_spaces = len(line) - len(ls)
        
        # if this is the first time we've seen an indent, then it's the indent length
        if line_spaces > 0 and indent_length is None: indent_length = line_spaces

        if line_spaces == 0:
            line_indents = 0
        else:
            line_indents = line_spaces / indent_length

        if line_indents > current_indents:
            prefixes.append(ls)
            current_indents = line_indents
        elif line_indents == current_indents:
            passes.append("/".join(prefixes))
            prefixes = prefixes[:-1]
            prefixes.append(ls)
        elif line_indents < current_indents:
            passes.append("/".join(prefixes))
            prefixes = prefixes[:line_indents-1]
            prefixes.append(ls)
            current_indents = line_indents

    results = [{
        "name": p,
        "key": p,
        "score": 90,
        "icon": "/usr/share/icons/Humanity/apps/48/password.svg",
        "description": "Password"
    } for p in passes if p]
    print json.dumps({"results": results})

def invoke(key):
    subprocess.Popen(["pass", "show", "-c", key])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print >> sys.stderr, "Bad invocation %r" % (sys.argv,)
    elif sys.argv[1] == "--query":
        query(sys.argv[2])
    elif sys.argv[1] == "--invoke":
        invoke(sys.argv[2])
    else:
        print >> sys.stderr, "Bad command %s" % (sys.argv[1],)
