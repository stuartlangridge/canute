#!/usr/bin/env python
import sys, json, subprocess
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk

def query(q):
    out = []
    icon = None
    deb = Gio.content_type_get_icon("application/vnd.debian.binary-package")
    if deb: 
        themeicon = Gtk.IconTheme.get_default().choose_icon(deb.get_names(), 512, 0)
        if themeicon:
            icon = themeicon.get_filename()
    o = subprocess.check_output(["apt-cache", "search", '^' + q])
    out = [{
        "name": line.split(" - ", 2)[0],
        "description": line.split(" - ", 2)[1],
        "key": line.split(" - ", 2)[0],
        "score": 10,
        "icon": icon
    } for line in o.split("\n") if line.strip() and " - " in line]
    print json.dumps({"results": out[:10]}) # don't bother returning more than 10

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print >> sys.stderr, "Bad invocation %r" % (sys.argv,)
    elif sys.argv[1] == "--query":
        query(sys.argv[2])
    elif sys.argv[1] == "--invoke":
        invoke(sys.argv[2])
    else:
        print >> sys.stderr, "Bad command %s" % (sys.argv[1],)
