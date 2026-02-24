# -*- coding: utf-8 -*-
# SatLodge WebPlus - Scarthgap Version (Python 3.12 Fix)
# Maintainer: SatLodge Team

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from Screens.Console import Console
from twisted.web.client import getPage
import os
import xml.etree.ElementTree as ET

# --- IMPORT SATLODGE CORE ---
try:
    from Plugins.Extensions.SatLodgeCore.slinfo import SatLodgeInfo
except ImportError:
    SatLodgeInfo = None

# --- METADATI ---
VERSION = "1.0.2"
XML_URL = "http://webplusfeeds.sat-lodge.it/xml/PluginEmulators.xml"
# FIX PER PYTHON 3.12: Usiamo una stringa normale, non bytes
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

class WebPlusScreen(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.skinName = "WebPlusScreen"
        
        self["header"] = Label("SatLodge WebPlus")
        self["list"] = MenuList([])
        self["status"] = Label("Caricamento lista...")
        self["info_box"] = Label("Info Sistema: Caricamento...")

        if SatLodgeInfo:
            self.sl_core = SatLodgeInfo()
        else:
            self.sl_core = None
        
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions"], {
            "ok": self.conferma,
            "cancel": self.close,
        }, -1)

        self.menu_list = []
        self.downloadXml()
        self.aggiornaInfo()

    def aggiornaInfo(self):
        if self.sl_core:
            try:
                modello = self.sl_core.getModel()
                ram = self.sl_core.getRamInfo()
                temp = self.sl_core.getCpuTemp()
                testo = "Box: %s  |  RAM: %s  |  Temp: %s" % (modello, ram, temp)
                self["info_box"].setText(testo)
            except:
                self["info_box"].setText("SatLodge Core: Errore lettura")
        else:
            self["info_box"].setText("SatLodge Core: Non trovato")

    def downloadXml(self):
        # Passiamo l'URL come stringa e l'agente codificato correttamente per Twisted
        getPage(XML_URL.encode('utf-8'), agent=UA.encode('utf-8'), timeout=10).addCallback(self.parseXml).addErrback(self.errorXml)

    def errorXml(self, error):
        self["status"].setText("Errore Download Lista")

    def parseXml(self, data):
        try:
            root = ET.fromstring(data)
            self.menu_list = []
            for item in root.findall(".//plugin"):
                name = item.get("name")
                url_node = item.find("url")
                if url_node is not None:
                    url = url_node.text.strip()
                    self.menu_list.append((name, url))
            self["list"].setList(self.menu_list)
            self["status"].setText("Versione %s - Seleziona e premi OK" % VERSION)
        except:
            self["status"].setText("Errore XML Server")

    def conferma(self):
        sel = self["list"].getCurrent()
        if sel:
            name = sel[0]
            url = sel[1]
            # Usiamo stringhe normali per i comandi
            if ".zip" in url.lower():
                cmd = 'wget --no-check-certificate -U "%s" "%s" -O /tmp/addon.zip ; unzip -o /tmp/addon.zip -d / ; wget -qO - http://127.0.0.1/web/servicelistreload?mode=0 ; rm -f /tmp/addon.zip' % (UA, url)
            else:
                cmd = 'wget --no-check-certificate -U "%s" "%s" -O /tmp/addon.ipk ; opkg install --force-overwrite --force-reinstall /tmp/addon.ipk ; rm -f /tmp/addon.ipk' % (UA, url)
            self.session.open(Console, title="Installazione %s" % name, cmdlist=[cmd])

def main(session, **kwargs):
    session.open(WebPlusScreen)

def Plugins(**kwargs):
    return [PluginDescriptor(name="SatLodge WebPlus", description="Download Emulators", where=PluginDescriptor.WHERE_PLUGINMENU, icon="plugin.png", fnc=main)]
