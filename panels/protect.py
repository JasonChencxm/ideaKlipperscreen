import logging
import gi
import configparser
import os

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Pango
from math import pi
from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel
from ks_includes.widgets.autogrid import AutoGrid
from ks_includes.KlippyGtk import find_widget

home = os.path.expanduser("~/")
printer_data_config = os.path.join(home, "printer_data", "config")
protection_config = os.path.join(printer_data_config, "protect.conf")

class Panel(ScreenPanel):
    def __init__(self, screen, title):
        title = title or _("Protect")
        super().__init__(screen, title)

        self.switch_button = Gtk.Switch()
        self.switch_button.connect("notify::active", self.on_switch_activated)
        self.grid = Gtk.Grid(column_spacing=10, row_spacing=5)
        self.grid.attach(self.switch_button, 0, 0, 1, 1)
        
        self.label = Gtk.Label(label=_("If you want to save the status, Please click the restart"))
        self.label.set_line_wrap(True)
        self.grid.attach(self.label, 1, 1, 1, 1)
        
        self.restart_button = self._gtk.Button("refresh", _("Restart"), "color3")
        self.restart_button.connect("clicked", self.on_restart_button_clicked)
        self.grid.attach(self.restart_button, 2, 2, 1, 1)
        
        config = configparser.ConfigParser()
        config.read(protection_config)
        if 'PrinterStatus' in config.sections():
            self._printer.status = config.getboolean('PrinterStatus', 'status')
        else:
            self._printer.status = None

        self.enter_interface()
        self.content.add(self.grid)
        
    def on_restart_button_clicked(self, button):
        try:
            os.system("sudo systemctl reboot -i")
            logging.info("Restart operation successful.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Restart operation failed: {e}")

    def on_switch_activated(self, switch, gparam):
        state = switch.get_active()
        if state:
            self._screen._ws.klippy.gcode_script('SET_PROTECT_ON')
            logging.info("The protection function is activated.")
        else:
            self._screen._ws.klippy.gcode_script('SET_PROTECT_OFF')
            logging.info("The protective function is disabled.")

        self._printer.status = state
        config = configparser.ConfigParser()
        config.read(protection_config)
        if not config.has_section('PrinterStatus'):
            config.add_section('PrinterStatus')
        config.set('PrinterStatus', 'status', str(self._printer.status))
        with open(protection_config, 'w') as configfile:
            config.write(configfile)

    def enter_interface(self):
        if self._printer.status is not None:
            self.switch_button.set_active(self._printer.status)