#!/usr/bin/env python

import urllib, json, os

# Fetch emojione definition file and output a Python plugin which searches it

fp = urllib.urlopen("https://raw.githubusercontent.com/Ranks/emojione/master/emoji.json")
data = fp.read()
fp.close()
emoji = json.loads(data)

by_shortname = dict(
    [
        (x["shortname"][1:-1], x["unicode"])
        for x in emoji.values()
        if "-" not in x["unicode"]
    ]
)

fp = open(os.path.join(os.path.split(__file__)[0], "emoji-plugin.py"))
data = fp.read()
fp.close()
fp = open(os.path.join(os.path.split(__file__)[0], "..", "plugins", "emoji.py"), "w")
fp.write(data.replace('{"nope": "1f600"}', str(by_shortname)))
fp.close()

