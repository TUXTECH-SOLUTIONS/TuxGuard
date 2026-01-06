import sys
import psutil
import socket
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gio, Adw, GLib, Gdk

CSS = """
window { background-color: #0a0a0a; }
label { color: #00ff41; font-family: 'Courier New', monospace; }
.title-label { font-size: 24px; font-weight: bold; color: #ffb000; }
.port-item { font-size: 13px; color: #00ff41; margin-bottom: 5px; }
button { 
    background: rgba(0, 255, 65, 0.1); 
    border: 1px solid #00ff41; 
    color: #00ff41; 
    padding: 10px;
    margin-top: 10px;
}
button:hover { background: #00ff41; color: #000; }
separator { background-color: #333; margin: 15px 0; }
"""

class TuxGuardApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id='io.kiber.tuxguard',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        display = Gdk.Display.get_default()
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS.encode())
        Gtk.StyleContext.add_provider_for_display(display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.win = Adw.ApplicationWindow(application=self)
        self.win.set_title("TuxGuard Security")
        self.win.set_default_size(450, 550)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.win.set_content(main_box)

        # Контейнер с отступами
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        box.set_margin_top(30)
        box.set_margin_bottom(30)
        box.set_margin_start(30)
        box.set_margin_end(30)
        main_box.append(box)

        title = Gtk.Label(label="> TUX_GUARD_v0.1")
        title.add_css_class("title-label")
        box.append(title)
        box.append(Gtk.Separator())

        self.status_label = Gtk.Label(label="SYSTEM NETWORK CHECK READY")
        box.append(self.status_label)

        # Прокручиваемый список портов
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_min_content_height(250)
        
        self.port_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        scrolled.set_child(self.port_list_box)
        box.append(scrolled)

        box.append(Gtk.Separator())

        self.btn_scan = Gtk.Button(label="[ SCAN OPEN PORTS ]")
        self.btn_scan.connect("clicked", self.on_scan_clicked)
        box.append(self.btn_scan)

        self.win.present()

    def on_scan_clicked(self, button):
        self.status_label.set_label("SCANNING ACTIVE CONNECTIONS...")
        # Очистка старого списка
        while self.port_list_box.get_first_child():
            self.port_list_box.remove(self.port_list_box.get_first_child())

        # Сканирование портов
        connections = psutil.net_connections(kind='inet')
        found = False
        
        for conn in connections:
            if conn.status == 'LISTEN':
                found = True
                port = conn.laddr.port
                try:
                    process = psutil.Process(conn.pid).name()
                except:
                    process = "Unknown"
                
                item = Gtk.Label(label=f"PORT {port} -> {process}")
                item.set_halign(Gtk.Align.START)
                item.add_css_class("port-item")
                self.port_list_box.append(item)

        if not found:
            self.port_list_box.append(Gtk.Label(label="NO OPEN PORTS FOUND"))
        
        self.status_label.set_label("SCAN COMPLETE")

if __name__ == "__main__":
    app = TuxGuardApp()
    app.run(sys.argv)
