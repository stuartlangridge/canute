#!/usr/bin/env python
import sys, json
import gi
import time
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk

def query(q):
    out = []
    results = Gio.DesktopAppInfo.search(q)
    if len(results) == 0:
        print json.dumps({"results": []})
        return
    scores = range(90, 10, int(-100 / (len(results)+1)))
    for apps in results:
        score = scores.pop(0)
        for app in apps:
            try:
                dai = Gio.DesktopAppInfo.new(app)
            except:
                continue
            icon = None
            gicon = dai.get_icon()
            if gicon:
                themeicon = None
                if hasattr(gicon, "get_names"):
                    themeicon = Gtk.IconTheme.get_default().choose_icon(gicon.get_names(), 512, 0)
                else:
                    themeicon = Gtk.IconTheme.get_default().choose_icon([gicon.to_string()], 512, 0)
                if themeicon:
                    icon = themeicon.get_filename()
            out.append({
                "name": dai.get_display_name(),
                "key": app,
                "score": score,
                "icon": icon,
                "description": dai.get_description()
            })
    print json.dumps({"results": out})

def invoke(key):
    appinfo = Gio.DesktopAppInfo.new(key)
    appinfo.launch()
    time.sleep(5) # give it time to start

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print >> sys.stderr, "Bad invocation %r" % (sys.argv,)
    elif sys.argv[1] == "--query":
        query(sys.argv[2])
    elif sys.argv[1] == "--invoke":
        invoke(sys.argv[2])
    else:
        print >> sys.stderr, "Bad command %s" % (sys.argv[1],)
