# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Interlis
                                 A QGIS plugin
 Interlis Import/Export
                              -------------------
        begin                : 2014-01-18
        copyright            : (C) 2014 by Pirmin Kalberer / Sourcepole
        email                : pka@sourcepole.ch
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# Import the PyQt and QGIS libraries
from qgis.PyQt.QtCore import QSettings, QCoreApplication, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QDockWidget
from qgis.core import QgsApplication
# Initialize Qt resources from file resources.py
from . import resources_rc
from .ogrtools.pyogr.ogrinfo import ogr_version_num
from .algorithms.interlis_provider import InterlisProvider
from .interlisdialog import InterlisDialog
import os.path


class Interlis:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(
            self.plugin_dir, 'i18n', 'interlis_{}.qm'.format(locale))

        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)
            QCoreApplication.installTranslator(self.translator)

        if ogr_version_num() < 2000200:
            raise ImportError("GDAL/OGR 2.0.2 or newer required")

        # Create the dialog (after translation) and keep reference
        self.dlg = InterlisDialog(self)
        # Processing provider
        self.provider = InterlisProvider()

    def initProcessing(self):
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/interlis/icon.png"),
            u"Interlis", self.iface.mainWindow())
        # connect the action to the run method
        self.action.triggered.connect(self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&Interlis", self.action)

        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&Interlis", self.action)
        self.iface.removeToolBarIcon(self.action)

    def messageLogWidget(self):
        return self.iface.mainWindow().findChild(QDockWidget, 'MessageLog')

    def run(self):
        self.dlg.setup()
        self.dlg.exec_()
