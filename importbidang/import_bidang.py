# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ImportBidang
                                 A QGIS plugin
 Import bidang ke Basisdata Bidang
                              -------------------
        begin                : 2017-02-08
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Septin Mulatsih Rezki
        email                : septinmulatsihrezki@gmail.com
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from import_bidang_dialog import ImportBidangDialog
from qgis.core import QgsMapLayer
import os.path
import psycopg2 #to connect postgres db


class ImportBidang:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ImportBidang_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = ImportBidangDialog()
        # connect slot
        self.dlg.cboLayer.currentIndexChanged.connect(self.index_changed)
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Import Bidang')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'ImportBidang')
        self.toolbar.setObjectName(u'ImportBidang')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('ImportBidang', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/ImportBidang/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Import Bidang'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Import Bidang'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def daftar_layer(self):
        """Function to get layer list from table of content

        :return: list of layer
        """
        daftar_layer = []
        for layer in self.iface.mapCanvas().layers():
            daftar_layer.append(layer)
        return daftar_layer

    def daftar_kolom(self, layer):
        """Function to get fields list of a layer

        :param layer:
        :return:
        """
        self.dlg.cboField.clear()
        if layer.type() == QgsMapLayer.VectorLayer:
            layer_fields = layer.pendingFields()
            for field in layer_fields:
                self.dlg.cboField.addItem(field.name(), field)


    def index_changed(self):
        """Mengakomodir perubahan layer terpilih terhadap daftar field yang akan ditampilkan"""
        current_index = self.dlg.cboLayer.currentIndex()
        layer = self.dlg.cboLayer.itemData(current_index)
        self.daftar_kolom(layer)

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        self.dlg.cboLayer.clear()
        daftar_layer = self.daftar_layer()
        for layer in daftar_layer:
            self.dlg.cboLayer.addItem(layer.name(), layer)
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            selectedLayerIndex = self.dlg.cboLayer.currentIndex()
            selectedLayer = self.iface.mapCanvas().layers()[selectedLayerIndex]
            #selectedLayer.setCrs(QgsCoordinateReferenceSystem(32750))
            #fields = selectedLayer.pendingFields()
            fieldname = str(self.dlg.cboField.currentText())

            for feature in selectedLayer.getFeatures():
                idx = selectedLayer.fieldNameIndex(fieldname)
                nop = feature.attributes()[idx]
                geom = feature.geometry()
                geom_wkt = geom.exportToWkt()
                #multipolygon = "MULTIPOLYGON((("
                geom_wkt_str = geom_wkt[10:-2]
                #st_geom = """ST_GeomFromText('"""
                #srid = """)', 32750)"""
                #geom_wkb_postgis = st_geom + multipolygon +geom_wkt_str + srid
                #wkb version, just return geometry, doesn't include SRID
                #geom_wkb = geom.asWkb()
                #geom_wkb_postgis = geom_wkb.encode('hex')
                query1 = '''INSERT INTO gis.tm_bidang3(d_nop,geom) VALUES (%s, ST_GeomFromText(%s, 32750));'''
                #query = """INSERT INTO gis.tm_bidang2(d_nop,geom) VALUES (%s, ST_GeomFromText('MULTIPOLYGON(((%s)))', 32750));"""
                data = [nop, geom_wkt]

                #Parameter Connection to database
                host_name = "localhost"
                port_name = "5433"
                db_name = "db_pbb"
                user_name = "postgres"
                user_pass = "septin"

                #Connection
                conn = psycopg2.connect("user='%s' password='%s' host='%s' port='%s' dbname='%s'" %
                                        (user_name, user_pass, host_name, port_name, db_name))
                cur = conn.cursor()
                cur.execute(query1, data)
                conn.commit()
                cur.close()
                conn.close()



