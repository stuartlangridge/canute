#!/usr/bin/env python
import sys, json, subprocess, mimetypes
try:
    from recoll import recoll
except ImportError:
    recoll = None

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk

def query(q):
    if not recoll:
        print json.dumps({"results": []})
        return

    mcache = {}
    db=recoll.connect()
    query=db.query()
    nres = query.execute(q)
    try:
        res = query.fetchmany(8)
    except:
        print json.dumps({"results": []})
        return
    out = []
    for r in res:
        title = r.title
        if not title: title = r.filename
        try:
            score = int(re.sub('[^0-9]', '', r.relevancyrating))
        except:
            score = 10
        icon = "/usr/share/icons/hicolor/48x48/apps/recoll.png"
        mimetype, encoding = mimetypes.guess_type(r.url)
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

        out.append({
            "name": title,
            "key": r.url,
            "score": score,
            "icon": icon,
            "description": r.abstract
        })

    print json.dumps({"results": out})

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
        print >> sys.stderr, "Bad command %s" % (sys.argv[1],)
