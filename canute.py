import sys, json, cgi, os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Keybinder', '3.0')

from gi.repository import Gio, Gtk, Gdk, GdkPixbuf, GLib
from gi.repository import Keybinder

class App(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self,
                                 application_id="org.kryogenix.canute",
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.connect("activate", self.activate)
        self.connect("startup", self.startup)

    def startup(self, app):
        self.window = Gtk.ApplicationWindow()
        self.app = app

        #self.window.set_type_hint(Gdk.WindowTypeHint.DOCK)
        screen = self.window.get_screen()
        rgba = screen.get_rgba_visual()
        self.window.set_visual(rgba)
        self.window.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(255, 255, 255, 1))
        self.window.set_position(Gtk.WindowPosition.CENTER)

        vb = Gtk.VBox()
        self.text_entry = Gtk.Entry()
        self.text_entry.connect("key-release-event", self.typing)
        self.text_entry.connect("key-press-event", self.trap_arrows)
        self.text_entry.set_size_request(400, -1)
        self.current_query = ""
        self.keypress_wait_timeout = None
        self.commands = Gtk.ListStore(
            str, # name
            GdkPixbuf.Pixbuf, #icon
            str, # plugin
            str, # plugin key
            int # score
        )
        v = Gtk.TreeView(self.commands)
        v.set_headers_visible(False)
        self.sel = v.get_selection()
        self.sel.set_mode(Gtk.SelectionMode.BROWSE)
        
        ricon = Gtk.CellRendererPixbuf()
        cicon = Gtk.TreeViewColumn("icon", ricon, pixbuf=1)
        v.append_column(cicon)
        rtitle = Gtk.CellRendererText()
        ctitle = Gtk.TreeViewColumn("text", rtitle, markup=0)
        v.append_column(ctitle)

        vb.pack_start(self.text_entry, False, True,0)
        hb = Gtk.HBox()
        hb.pack_start(v, True, True, 12)
        vb.pack_start(hb, True, True, 0)
        self.window.add(vb)

        app.add_window(self.window)
        keystr = "<Ctrl><Alt>M"
        print "Activation key:", keystr
        Keybinder.init()
        Keybinder.bind(keystr, self.key_activate)

        style_provider = Gtk.CssProvider()
        css = """
            GtkWindow {
                border: 3px solid #c0ffee;
            }
            GtkEntry {
                font-size: 300%;
                border: 3px solid #ac1d1c;
            }
        """
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), 
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def trap_arrows(self, entry, key):
        if key.keyval == Gdk.KEY_Down:
            model, paths = self.sel.get_selected_rows()
            if len(paths) == 0 and len(model) > 0:
                p = 0
            else:
                p = (int(paths[0].to_string()) + 1) % len(model)
            self.sel.select_path(Gtk.TreePath.new_from_string(str(p)))
            return True
        elif key.keyval == Gdk.KEY_Up:
            model, paths = self.sel.get_selected_rows()
            if len(paths) == 0 and len(model) > 0:
                p = len(model) - 1
            else:
                p = (int(paths[0].to_string()) - 1) % len(model)
                if p < 0: p = len(model) - p
            self.sel.select_path(Gtk.TreePath.new_from_string(str(p)))
            return True
        elif key.keyval == Gdk.KEY_Return:
            model, it = self.sel.get_selected()
            plugin = model.get_value(it, 2)
            key = model.get_value(it, 3)
            print "Execute", plugin, key
            self.window.hide()
            proc = Gio.Subprocess.new([plugin, "--invoke", key], Gio.SubprocessFlags.NONE)
            if key.startswith("special_") and hasattr(self, "execute_%s" % key):
                getattr(self, "execute_%s" % key)()
            return True
        return False

    def execute_special_restart(self):
        os.system("bash -c 'sleep 2 && python %s' &" % (sys.argv[0],))
        self.app.quit()

    def typing(self, entry, key):
        if key.keyval == Gdk.KEY_Escape:
            self.window.hide()
            return
        txt = entry.get_text()
        if txt == self.current_query:
            pass
        else:
            self.current_query = txt
            # start timer; we wait until a bit after the last keypress before starting
            # plugins, so that typing a long string doesn't invoke them all needlessly
            if self.keypress_wait_timeout: GLib.source_remove(self.keypress_wait_timeout)
            self.keypress_wait_timeout = GLib.timeout_add(200, self.populate_list, txt)

    def key_activate(self, keystr):
        self.window.show_all()
        self.window.set_decorated(False)
        self.window.present_with_time(Keybinder.get_current_event_time())
        self.populate_list(self.text_entry.get_text())
        self.text_entry.grab_focus()

    def populate_list(self, query):
        self.keypress_wait_timeout = None # so we don't try to clear this timeout when it's run already
        self.commands.clear()
        if not query.strip(): return
        f = Gio.File.new_for_path("/home/aquarius/Programs/Mine/canute/plugins/")
        f.enumerate_children_async("access::can-execute,standard::*", 
            Gio.FileQueryInfoFlags.NONE, GLib.PRIORITY_DEFAULT, None, 
            self.plugins_list, query)
    def plugins_list(self, f, result, query):
        en = f.enumerate_children_finish(result)
        while 1:
            nxt = en.next_file()
            if not nxt: break
            if nxt.get_attribute_boolean(Gio.FILE_ATTRIBUTE_ACCESS_CAN_EXECUTE):
                plugin = en.get_child(nxt).get_path()
                proc = Gio.Subprocess.new([plugin, "--query", query],
                    Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_PIPE)
                proc.communicate_utf8_async(None, None, self.plugin_result, [plugin, query])
    def plugin_result(self, proc, result, userdata):
        plugin, query = userdata
        ok, stdout, stderr = proc.communicate_utf8_finish(result)
        if ok and stdout:
            if query == self.current_query:
                output = None
                try:
                    output = json.loads(stdout)
                except:
                    stderr = "Invalid JSON (%s)" % stdout
                if output:
                    for result in output.get("results", []):
                        self.insert_into_list(result, plugin)
        if stderr:
            print "plugin error", plugin, stderr

    def insert_into_list(self, result, plugin):
        MAX_LIST_LENGTH = 8
        clen = len(self.commands)
        minscore = 0
        if clen > 0:
            minscore = self.commands[len(self.commands)-1][4]
        if clen >= MAX_LIST_LENGTH and minscore > result["score"]:
            return
        idx = 0
        insertidx = -1
        if clen == 0:
            insertidx = 0
        else:
            for row in self.commands:
                if row[4] < result["score"]:
                    insertidx = idx
                    break
                idx += 1

        if insertidx == -1:
            if clen == MAX_LIST_LENGTH:
                return
            else:
                insertidx = clen

        if result["icon"]:
            pb = GdkPixbuf.Pixbuf.new_from_file_at_size(result["icon"], 32, 32)
        else:
            pb = None
        desc = result["description"]
        if not desc: desc = " "
        if len(desc) > 50:
            desc = desc[:19] + "..."
        self.commands.insert(insertidx, [
            "<big>%s</big>\n<small>%s</small>" % (cgi.escape(result["name"]), cgi.escape(desc)),
            pb,
            plugin,
            result["key"],
            result["score"]
        ])
        while len(self.commands) > MAX_LIST_LENGTH:
            self.commands.remove(self.commands.get_iter_from_string(str(MAX_LIST_LENGTH)))

    def activate(self, app):
        print "activated"

if __name__ == '__main__':
    app = App()
    app.run(sys.argv)
