#!/usr/bin/env python
import sys, json, subprocess, os, glob, re
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk

ansi_escape = re.compile(r'\x1b[^m]*m')

def query(q):
    if not os.path.exists("/usr/bin/snap"):
        print json.dumps({"results": []})
        return
    o = subprocess.check_output(["snap", "find", q])
    if "no snaps found" in o:
        print json.dumps({"results": []})
        return

    debicon = None
    deb = Gio.content_type_get_icon("application/vnd.debian.binary-package")
    if deb: 
        themeicon = Gtk.IconTheme.get_default().choose_icon(deb.get_names(), 512, 0)
        if themeicon:
            debicon = themeicon.get_filename()

    current = {}
    out = []
    lines = o.split("\n")
    header = lines[0]
    results = lines[1:]
    startwords = []
    inword = False
    for idx, ch in enumerate(list(header)):
        if ch == " ":
            inword = False
        else:
            if not inword:
                startwords.append(idx)
                inword = True
    slices = []
    for i in range(len(startwords)):
        if i == len(startwords) - 1:
            slices.append((startwords[i], None))
        else:
            slices.append((startwords[i], startwords[i+1]-1))
    names = [header[a[0]:a[1]].strip() for a in slices]

    out = []
    for line in results:
        if not line.strip(): continue
        parts = [line[a[0]:a[1]].strip() for a in slices]
        out.append(dict(zip(names, parts)))

    out = [
        {
            "name": "Install snap: %s (%s)" % (x.get("Name", "unknown snap"),x.get("Version", "latest")),
            "description": "Ready to install (%s)" % (x.get("Summary", "via gnome-software"),),
            "score": 50,
            "icon": debicon,
            "key": x.get("Name", "unknown")
        }
        for x in out
    ]

    print json.dumps({"results": out})

def invoke(key):
    subprocess.Popen(["gnome-software", "--search=%s" % key])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print >> sys.stderr, "Bad invocation %r" % (sys.argv,)
    elif sys.argv[1] == "--query":
        query(sys.argv[2])
    elif sys.argv[1] == "--invoke":
        invoke(sys.argv[2])
    else:
        print >> sys.stderr, "Bad command %s" % (sys.argv[1],)
