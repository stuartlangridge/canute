#!/usr/bin/env python
import sys, json, subprocess, os, glob, re
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk

ansi_escape = re.compile(r'\x1b[^m]*m')

def query(q):
    if not os.path.exists("/usr/bin/appstreamcli"):
        print json.dumps({"results": []})
        return
    o = subprocess.check_output(["appstreamcli", "search", q])
    if "No component matching" in o:
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
    for line in o.split("\n"):
        if "----" in line:
            out.append(current)
            current = {}
        else:
            parts = line.strip().split(":", 2)
            if len(parts) == 2:
                current[ansi_escape.sub('', parts[0].strip())] = ansi_escape.sub('', parts[1].strip())

    out = [
        {
            "name": "Install: %s" % (x.get("Name", "unknown app"),),
            "description": "Ready to install (%s)" % (x.get("Summary", "via gnome-software"),),
            "score": 50,
            "icon": x.get("Icon"),
            "key": x.get("Package", "unknown")
        }
        for x in out
    ]

    for x in out:
        icons = glob.glob("/var/lib/app-info/icons/*/64x64/%s" % x["icon"])
        if not icons:
            x["icon"] = debicon
        else:
            x["icon"] = icons[0]

    print json.dumps({"results": out})

def invoke(key):
    subprocess.Popen(["gnome-software", "--details-pkg=%s" % key])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print >> sys.stderr, "Bad invocation %r" % (sys.argv,)
    elif sys.argv[1] == "--query":
        query(sys.argv[2])
    elif sys.argv[1] == "--invoke":
        invoke(sys.argv[2])
    else:
        print >> sys.stderr, "Bad command %s" % (sys.argv[1],)
