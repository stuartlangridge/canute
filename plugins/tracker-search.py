#!/usr/bin/env python3
import sys, json, subprocess, mimetypes, urllib, os, re

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Tracker', '1.0')
from gi.repository import Gio, Gtk, Tracker

def query(q):
    sparql = ("SELECT fts:rank(?f) nie:url(?f) fts:snippet(?f, '', '', '', 3)"
        "WHERE { ?f fts:match '\"%s\"' } order by desc(fts:rank(?f))") % q
    conn = Tracker.SparqlConnection.get (None)
    cursor = conn.query (sparql, None)

    results = []
    mcache = {}
    while (cursor.next(None)):
        if len(results) > 10: break
        score = int(float(cursor.get_string(0)[0]))
        url = cursor.get_string(1)[0]
        description = re.sub("\W+", " ", cursor.get_string(2)[0])
        filename = urllib.parse.unquote(url)[7:]

        icon = "/usr/share/icons/hicolor/48x48/apps/tracker.png"
        mimetype, encoding = mimetypes.guess_type(filename)
        if mimetype:
            cached = mcache.get(mimetype)
            if cached:
                icon = cached
            else:
                gio_icon_name = Gio.content_type_get_icon(mimetype)
                if gio_icon_name:
                    themeicon = Gtk.IconTheme.get_default().choose_icon(gio_icon_name.get_names(), 512, 0)
                    if themeicon:
                        icon = themeicon.get_filename()
                        mcache[mimetype] = icon

        results.append({
            "name": os.path.split(filename)[1],
            "key": filename,
            "score": score,
            "icon": icon,
            "description": description
        })

    print(json.dumps({"results": results}))

def invoke(key):
    subprocess.Popen(["nautilus", key])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print >> sys.stderr, "Bad invocation %r" % (sys.argv,)
    elif sys.argv[1] == "--query":
        query(sys.argv[2])
    elif sys.argv[1] == "--invoke":
        invoke(sys.argv[2])
    else:
        print("Bad command %s" % (sys.argv[1],), file=sys.stderr)
