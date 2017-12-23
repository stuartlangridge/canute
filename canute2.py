#!/usr/bin/env python3

"""
Canute
A simple desktop launcher which runs plugins at runtime and doesn't index
"""

import sys, os, random, json, time
from PyQt5.QtWidgets import QApplication, QDesktopWidget
from PyQt5.QtQml import QQmlApplicationEngine, QQmlEngine, QQmlComponent
from PyQt5.QtCore import (QAbstractListModel, Qt, pyqtSlot, QDir, 
    QSortFilterProxyModel, QProcess, QTimer, QModelIndex)
from PyQt5.QtGui import QKeySequence

from shortyQt import Shorty

class SortedShortenedSearchResults(QSortFilterProxyModel):
    @pyqtSlot(str)
    def search_input(self, q):
        return self.sourceModel().search_input(q)

    @pyqtSlot(int)
    def invoke(self, row_index):
        sm = self.sourceModel()
        qmi = self.index(row_index, 0, QModelIndex())
        data = dict([(role[1], self.data(qmi, role[0])) for role in sm._roles.items()])
        return sm.invoke_data(data)

    def filterAcceptsRow(self, source_row_idx, source_parent):
        index = self.sourceModel().index(source_row_idx, 0, source_parent)
        data = repr([self.sourceModel().data(index, Qt.UserRole + k) for k in range(1,6)])
        #print("filtering?", source_row_idx, index, data)
        if source_row_idx > 10: return False
        return super(SortedShortenedSearchResults, self).filterAcceptsRow(
            source_row_idx, source_parent)

class SearchResults(QAbstractListModel):
    NameRole = Qt.UserRole + 1
    KeyRole = Qt.UserRole + 2
    ScoreRole = Qt.UserRole + 3
    IconRole = Qt.UserRole + 4
    DescriptionRole = Qt.UserRole + 5
    PluginRole = Qt.UserRole + 6

    _roles = {NameRole: b"name", KeyRole: b"key", ScoreRole: b"score",
        IconRole: b"icon", DescriptionRole: b"description",
        PluginRole: b"plugin"}

    def __init__(self):
        super(SearchResults, self).__init__()
        self.plugin_dir = QDir(os.path.join(os.path.split(__file__)[0], "plugins"))
        self.plugin_dir.setFilter(QDir.Files | QDir.Executable)
        self._results = []
        self._processes = []

    def add_results(self, results):
        # We need to add to our internal list, and then fire events so
        # everyone knows we've added it
        # It doesn't need to be added in order; the SortedShortenedSearchResults
        # model takes care of that
        first = len(self._results)
        last = len(self._results) + len(results) - 1
        self.beginInsertRows(QModelIndex(), first, last), 
        self._results += results
        self.endInsertRows()

    def process_finished(self, process, plugin, q, exitcode, exitstatus):
        if exitstatus == QProcess.CrashExit:
            if exitcode == 9:
                # SIGKILL, meaning we killed it because a new query came in
                return
            stderr = str(process.readAllStandardError(), encoding="utf-8")
            print("Plugin error (%s) from %s for query '%s'\n%s\n" % (
                exitcode, plugin, q, stderr))
            return

        stdout = str(process.readAllStandardOutput(), encoding="utf-8")
        #print("from plugin", plugin, "query", q, "\n", stdout[:150])
        try:
            j = json.loads(stdout)
        except:
            print("JSON load error from plugin %s for query '%s'\n'%s'" % (
                plugin, q, stdout[:50]))
            return
        results = j.get("results")
        if results:
            r = results[:10] # never any point passing more than 10
            for rr in r: rr["plugin"] = plugin
            self.add_results(r)

    def query_plugin(self, plugin, q):
        #print("Calling", plugin)
        p = QProcess(self)
        self._processes.append(p)
        p.start(plugin, ["--query", q])

        p.finished.connect(lambda ec, es: self.process_finished(p, plugin, q, ec, es))

    def query_plugins(self, q):
        plugin_list = self.plugin_dir.entryList()

        # if the first word is actually the name of a plugin, then
        # run that one only
        words = q.split()
        if len(words) > 1:
            for p in plugin_list:
                base = os.path.splitext(os.path.basename(p))[0]
                if base == words[0]:
                    self.query_plugin(self.plugin_dir.filePath(p), " ".join(words[1:]))
                    return
        for p in plugin_list:
            self.query_plugin(self.plugin_dir.filePath(p), q)

    def update(self, q):
        self.beginResetModel()
        self._results = []
        while self._processes: self._processes.pop(0).kill()
        if q.strip() and len(q.strip()) > 2: self.query_plugins(q)
        self.endResetModel()

    @pyqtSlot(str)
    def search_input(self, q):
        self.update(q)

    def invoke_data(self, data):
        print("invoking", data)

        if data[b"key"].startswith("special_") and hasattr(self, "execute_%s" % data[b"key"]):
            getattr(self, "execute_%s" % data[b"key"])()
            return

        p = QProcess(self)
        p.start(data[b"plugin"], ["--invoke", data[b"key"]])

    def execute_special_restart(self):
        executable = sys.executable
        args = sys.argv[:]
        args.insert(0, sys.executable)
        time.sleep(1)
        print("Respawning")
        os.execvp(executable, args)

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self._results)

    def data(self, QModelIndex, role=None):
        row = QModelIndex.row()
        if role:
            rolename = self._roles.get(role)
            if rolename:
                val = self._results[row].get(rolename.decode("utf-8"))
                return val
        return

    def roleNames(self):
        return self._roles


def reveal(win):
    win.setVisible(True)
    win.showNormal()
    print("summon")


def main():

    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    context = engine.rootContext()
    model = SearchResults()
    sortedModel = SortedShortenedSearchResults()
    sortedModel.setSourceModel(model)
    sortedModel.setSortRole(model.ScoreRole)
    sortedModel.sort(0, Qt.DescendingOrder)
    context.setContextProperty("pyresults", sortedModel)
    engine.load(os.path.join(os.path.split(__file__)[0], 'canute2.qml')) # must load once we've assigned the model

    SHORTCUT_SHOW = QKeySequence("Ctrl+Alt+M")
    show = Shorty(SHORTCUT_SHOW)
    win = engine.rootObjects()[0]
    show.activated.connect(lambda: reveal(win))
    show.enable()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
