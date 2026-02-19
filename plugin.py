# -*- coding: utf-8 -*-
# SatLodge WebPlus - Scarthgap Version
# Maintainer: SatLodge Team

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from Screens.Console import Console
import os
import xml.etree.ElementTree as ET

# --- METADATI ---
VERSION = "1.0.1"
XML_URL = "http://webplusfeeds.sat-lodge.it/xml/PluginEmulators.xml"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

class SatLodgePanel(Screen):
    skin = """
        <screen name="SatLodgePanel" position="center,center" size="1200,850" title="SatLodge WebPlus v%s" backgroundColor="#101010">
            <eLabel position="0,0" size="1200,100" backgroundColor="#1a1a1a" zPosition="-1" />
            <widget name="header" position="40,25" size="1120,50" font="Regular;45" halign="left" transparent="1" foregroundColor="#ffffff" />
            <widget name="logo" position="center,130" size="400,400" alphatest="on" />
            <widget name="menu" position="100,530" size="1000,250" itemHeight="60" font="Regular;32" scrollbarMode="showOnDemand" />
            <widget name="status" position="center,795" size="1100,40" font="Regular;30" halign="center" foregroundColor="#ffcc00" transparent="1" />
        </screen>""" % VERSION

    def __init__(self, session):
        Screen.__init__(self, session)
        self["header"] = Label("SATLODGE WEBPLUS PRO")
        self["logo"] = Pixmap()
        self["status"] = Label("Caricamento lista...")
        self["menu"] = MenuList([])
        self.menu_list = []
        self["actions"] = ActionMap(["OkCancelActions"], {"ok": self.conferma, "cancel": self.close}, -1)
        self.onLayoutFinish.append(self.avvio)

    def avvio(self):
        # Percorso dinamico per il logo
        p = os.path.dirname(__file__) + "/plugin.png"
        if os.path.exists(p):
            self["logo"].instance.setPixmapFromFile(p)
        self.scarica_lista()

    def scarica_lista(self):
        target = "/tmp/sl_feeds.xml"
        cmd = 'wget --no-check-certificate -U "%s" "%s" -O %s' % (UA, XML_URL, target)
        os.system(cmd)
        self.popola_menu(target)

    def popola_menu(self, path):
        if os.path.exists(path) and os.path.getsize(path) > 100:
            try:
                tree = ET.parse(path)
                root = tree.getroot()
                self.menu_list = []
                for item in root.findall(".//plugin"):
                    name = item.get("name")
                    url_node = item.find("url")
                    if url_node is not None:
                        url = url_node.text.strip()
                        self.menu_list.append((name, url))
                self["menu"].setList(self.menu_list)
                self["status"].setText("Versione %s - Seleziona e premi OK" % VERSION)
            except:
                self["status"].setText("Errore XML Server")
        else:
            self["status"].setText("Errore Download Lista")

    def conferma(self):
        sel = self["menu"].getCurrent()
        if sel:
            name = sel[0]
            url = sel[1]
            if ".zip" in url.lower():
                cmd = 'wget --no-check-certificate -U "%s" "%s" -O /tmp/addon.zip ; unzip -o /tmp/addon.zip -d / ; wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 ; rm -f /tmp/addon.zip' % (UA, url)
            else:
                cmd = 'wget --no-check-certificate -U "%s" "%s" -O /tmp/addon.ipk ; opkg install --force-overwrite --force-reinstall /tmp/addon.ipk ; rm -f /tmp/addon.ipk' % (UA, url)
            self.session.open(Console, title="Installazione %s" % name, cmdlist=[cmd])

def main(session, **kwargs):
    session.open(SatLodgePanel)

def Plugins(**kwargs):
    return [PluginDescriptor(name="SatLodge WebPlus", description="v%s Addon Manager" % VERSION, where=PluginDescriptor.WHERE_PLUGINMENU, icon="plugin.png", fnc=main)]
