#!/usr/bin/env python3
import fcntl
import json
import os
import pwd
import re
import subprocess
import sys
import threading
import time
import urllib.request
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

import gi
gi.require_version("AyatanaAppIndicator3", "0.1")
from gi.repository import AyatanaAppIndicator3, GLib, Gtk  # noqa: E402

LOCK_FILE = os.path.expanduser("~/.cache/cyberghost-indicator.lock")
ICON_THEME_PATH = os.path.expanduser("~/.local/share/icons/cyberghost-indicator")
ICON_ON = "vpn-on"
ICON_OFF = "vpn-off"

POPULAR_COUNTRIES = {
    "Italia": "it",
    "Germania": "de",
    "Paesi Bassi": "nl",
    "Francia": "fr",
    "Spagna": "es",
    "Svizzera": "ch",
    "Regno Unito": "gb",
    "Stati Uniti": "us",
}


def acquire_lock():
    os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)
    fd = os.open(LOCK_FILE, os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("CyberGhost indicatore: gia' in esecuzione.")
        sys.exit(0)
    os.ftruncate(fd, 0)
    os.write(fd, str(os.getpid()).encode())
    return fd


def current_user():
    try:
        return pwd.getpwuid(os.getuid()).pw_name
    except Exception:
        return os.environ.get("USER", "andrea")


def run_root(args):
    cmd = ["pkexec", "env", "SUDO_USER=%s" % current_user(),
           "USER=%s" % current_user(), "cyberghostvpn"] + args
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def has_tun():
    try:
        out = subprocess.run(["ip", "-o", "link", "show", "type", "tun"],
                             capture_output=True, text=True, timeout=10)
        return bool(out.stdout.strip())
    except Exception:
        return False


def is_connected():
    if has_tun():
        return True
    try:
        out = subprocess.run(["cyberghostvpn", "--status"],
                             capture_output=True, text=True, timeout=15)
        if "VPN connection found" in out.stdout:
            return True
    except Exception:
        pass
    return False


def get_vpn_server():
    try:
        out = subprocess.run(["pgrep", "-af", "openvpn"],
                             capture_output=True, text=True, timeout=10)
        m = re.search(r"--remote\s+(\S+)\s+(\d+)", out.stdout)
        if m:
            host = m.group(1)
            port = m.group(2)
            name = host.split(".")[0]
            return name, host, port
    except Exception:
        pass
    return None, None, None


def _http_json(url):
    req = urllib.request.Request(url,
                                 headers={"User-Agent": "cyberghost-indicator/1.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())


def get_geo():
    try:
        d = _http_json("https://ipwho.is/")
        if d.get("success"):
            return (d.get("ip"), d.get("city"), d.get("country"),
                    (d.get("connection") or {}).get("isp"))
    except Exception:
        pass
    try:
        d = _http_json("http://ip-api.com/json/?fields=status,query,country,city,isp")
        if d.get("status") == "success":
            return d.get("query"), d.get("city"), d.get("country"), d.get("isp")
    except Exception:
        pass
    return None, None, None, None


def dbg(msg):
    if not os.environ.get("CG_DEBUG"):
        return
    try:
        with open("/tmp/cg-indicator.log", "a") as f:
            f.write("%s %s\n" % (time.strftime("%H:%M:%S"), msg))
    except Exception:
        pass


def notify(title, text):
    try:
        subprocess.Popen(["notify-send", "-i", "network-vpn", title, text],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


class Indicator:
    def __init__(self):
        self.ind = AyatanaAppIndicator3.Indicator.new(
            "cyberghost-indicator", ICON_OFF,
            AyatanaAppIndicator3.IndicatorCategory.APPLICATION_STATUS)
        self.ind.set_icon_theme_path(ICON_THEME_PATH)
        self.ind.set_status(AyatanaAppIndicator3.IndicatorStatus.ACTIVE)
        self.connected = None
        self.geo = None
        self._geo_server = None
        self.server_name = None
        self._last_server = None
        self.last_geo_fetch = 0
        self.home_ip = None
        self._last_home_ip_fetch = 0
        self.build_menu()
        self.refresh()
        GLib.timeout_add_seconds(5, self.refresh)

    def set_icon(self, connected):
        icon = ICON_ON if connected else ICON_OFF
        self.ind.set_icon_full(icon, "CyberGhost " + ("ON" if connected else "OFF"))
        self.ind.set_attention_icon_full(icon, "CyberGhost")

    def _mk_item(self, label, tooltip=None):
        item = Gtk.MenuItem(label=" ")
        item.set_sensitive(False)
        if tooltip:
            try:
                item.set_tooltip_text(tooltip)
            except Exception:
                pass
        self.menu.append(item)
        self.menu.show_all()
        return item.get_child()

    def build_menu(self):
        self.menu = Gtk.Menu()

        self.status_label = self._mk_item("Verifica...")
        self.server_label = self._mk_item(" ")
        self.geo_label = self._mk_item(" ")
        self.ip_label = self._mk_item(" ")

        self.menu.append(Gtk.SeparatorMenuItem())

        item = Gtk.MenuItem(label="Disconnetti")
        item.connect("activate", lambda w: run_root(["--stop"]))
        self.disconnect_item = item
        self.menu.append(item)

        sub = Gtk.MenuItem(label="Connetti a...")
        submenu = Gtk.Menu()
        for name, code in POPULAR_COUNTRIES.items():
            it = Gtk.MenuItem(label="%s  (%s)" % (name, code))
            it.connect("activate",
                       lambda w, c=code: run_root(["--country-code", c, "--connect"]))
            submenu.append(it)
        sub.set_submenu(submenu)
        self.menu.append(sub)

        self.menu.append(Gtk.SeparatorMenuItem())

        item = Gtk.MenuItem(label="Aggiorna stato")
        item.connect("activate", lambda w: self.refresh())
        self.menu.append(item)

        item = Gtk.MenuItem(label="Esci")
        item.connect("activate", lambda w: Gtk.main_quit())
        self.menu.append(item)

        self.menu.show_all()
        self.ind.set_menu(self.menu)

    def refresh(self):
        conn = is_connected()
        if self.connected is not None and conn != self.connected:
            notify("CyberGhost VPN", "Connessione VPN " +
                   ("attiva" if conn else "terminata"))
        self.connected = conn
        self.set_icon(conn)
        self.disconnect_item.set_sensitive(conn)

        self.status_label.set_text("VPN ATTIVA" if conn else "VPN NON ATTIVA")

        if conn:
            self.server_name, host, port = get_vpn_server()
            if host:
                self.server_label.set_text("Server: %s (%s:%s)" % (self.server_name, host, port))
                self.server_label.set_line_wrap(True)
                self.server_label.show()
                if self.server_name != self._last_server:
                    dbg("server cambiato: %s -> %s (azzero geo)" % (self._last_server, self.server_name))
                    self._last_server = self.server_name
                    self.last_geo_fetch = 0
                    self.geo = None
                    self._geo_server = None
            else:
                self.server_label.set_text("Server: ?")
                self.server_label.show()

            now = time.time()
            if self.geo is None or self._geo_server != self._last_server:
                if now - self.last_geo_fetch > 1.5:
                    self.last_geo_fetch = now
                    threading.Thread(target=self._fetch_geo, daemon=True).start()
                self.ip_label.set_text("IP: rilevamento...")
                self.geo_label.set_text("Posizione: rilevamento...")
            elif now - self.last_geo_fetch > 8:
                self.last_geo_fetch = now
                threading.Thread(target=self._fetch_geo, daemon=True).start()
                ip, city, country, isp = self.geo
                self.ip_label.set_text("IP: %s" % ip)
                pos = ", ".join(x for x in (city, country) if x)
                self.geo_label.set_text("Posizione: %s" % pos if pos else "Posizione: ?")
            else:
                ip, city, country, isp = self.geo
                self.ip_label.set_text("IP: %s" % ip)
                pos = ", ".join(x for x in (city, country) if x)
                self.geo_label.set_text("Posizione: %s" % pos if pos else "Posizione: ?")
                dbg("display server=%s ip=%s pos=%s" % (self.server_name, ip, pos or "?"))
            self.geo_label.show()
            self.ip_label.show()
        else:
            self.server_name = None
            self.geo = None
            self._geo_server = None
            self._last_server = None
            self.server_label.hide()
            self.geo_label.hide()
            self.ip_label.hide()
            now = time.time()
            if now - self._last_home_ip_fetch > 30:
                self._last_home_ip_fetch = now
                threading.Thread(target=self._update_home_ip, daemon=True).start()
        return True

    def _update_home_ip(self):
        ip, city, country, isp = get_geo()
        if ip and is_connected() is False:
            self.home_ip = ip
            dbg("IP di casa rilevato: %s" % ip)

    def _fetch_geo(self):
        ip, city, country, isp = get_geo()
        dbg("geo fetch -> ip=%s city=%s country=%s (home_ip=%s)" % (ip, city, country, self.home_ip))
        if not ip:
            return
        if not is_connected():
            dbg("geo scartata: tunnel non attivo durante il rilevamento (evita falso Milan)")
            return
        if self.home_ip and ip == self.home_ip:
            dbg("geo scartata: IP uguale all'IP di casa (%s) = transizione, non server" % ip)
            return
        server = self.server_name
        GLib.idle_add(self._apply_geo, (ip, city, country, isp), server)

    def _apply_geo(self, geo, server):
        self.geo = geo
        self._geo_server = server
        if self.connected and server == self._last_server:
            ip, city, country, isp = geo
            self.ip_label.set_text("IP: %s" % ip)
            pos = ", ".join(x for x in (city, country) if x)
            self.geo_label.set_text("Posizione: %s" % pos if pos else "Posizione: ?")
            dbg("display server=%s ip=%s pos=%s" % (self.server_name, ip, pos or "?"))
        return False


def main():
    global LOCK_FD
    LOCK_FD = acquire_lock()
    Gtk.init(None)
    Indicator()
    Gtk.main()


if __name__ == "__main__":
    main()
