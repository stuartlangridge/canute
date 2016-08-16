#!/usr/bin/env python
import sys, json, subprocess
try:
    from recoll import recoll
except ImportError:
    recoll = None

def query(q):
    if not recoll:
        print json.dumps({"results": []})
        return

    db=recoll.connect()
    query=db.query()
    nres = query.execute(q)
    res = query.fetchmany(5)
    out = []
    for r in res:
        title = r.title
        if not title: title = r.filename
        try:
            score = int(re.sub('[^0-9]', '', r.relevancyrating))
        except:
            score = 10
        out.append({
            "name": title,
            "key": r.url,
            "score": score,
            "icon": "/usr/share/icons/hicolor/48x48/apps/recoll.png",
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
