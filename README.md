# A tiny keyboard launcher

Warning: this was written by Stuart for Stuart. It has a whole bunch of hardcoded non-customisable stuff. If people really want this app to be customisable, let me know and I'll think about it.

Like Albert or Mutate or a bunch of other things. Does no indexing or anything itself; instead, Canute relies on plugins. A plugin can be written in any language. When one presses the Canute hotkey (`Ctrl`-`Alt`-`M`), the Canute search box pops up. Entering a search runs all the plugins and shows the top 8 results.

## Plugins

A plugin is an executable file, which lives in the `plugins` folder. To do a search, it is started as `pluginname --query "the query"` and is expected to return JSON which looks like

```
{
    results: [
        {
            "name": "Some Value",
            "description": "A longer description of this matching thing",
            "score": 100, # can be 0 - 100, where 100 is the best match and 0 is not good at all
            "icon": "/home/fred/someimg.png", # full path to an image file
            "key": "unique-key-for-result"
        },
        ...
    ]
}
```

There's no point in returning a million results because Canute will onyl display the top 8 or so anyway.

If a result is chosen, the plugin is started as `pluginname --invoke unique-key-for-result`, at which point it should do whatever's sensible to display that result.

## Supplied plugins

In the plugins folder are some easy-to-understand examples, which does calculations (`2+5/3`), search installed applications, search `apt` for packages, and connect to an existing [recoll](http://www.lesbonscomptes.com/recoll) server for full text search.

## Using the Super key to launch Canute

* Install ksuperkey (on Ubuntu, from [the mehanik PPA](https://launchpad.net/~mehanik/+archive/ubuntu/ksuperkey))
* Run (possibly from Startup Applications) `ksuperkey -e 'Super_L=Control_L|Alt_L|M'`
* run Ubuntu Tweak and change the Dash's hotkey to be something else, otherwise you'll get Canute _and_ the Dash

(thank you to [the Albert wiki](https://github.com/ManuelSchneid3r/albert/wiki/By-users-for-users#launch-albert-via-single-supermetawindows-key-an-easy-workaround) for these instructions)

