# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PluginSyncQGISGeoServer
                                 A QGIS plugin
 El plugin personalizado "SyncQGISGeoServer" facilita la sincronización bidireccional de datos entre QGIS y GeoServer, permitiendo exportar capas desde QGIS a GeoServer y visualizar capas desde GeoServer en QGIS mediante servicios WFS.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-06-27
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Innovacion DPVER
        email                : innovaciondpver@gmail.com
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
import os
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.core import QgsProject, QgsVectorLayer, QgsVectorFileWriter
import requests
from .sync_qgis_geoserver_dialog import AuthenticationDialog, PluginSyncQGISGeoServerDialog

class PluginSyncQGISGeoServer:
    """Implementación del Plugin QGIS para sincronización con GeoServer."""

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.username = None
        self.password = None

    def tr(self, message):
        return QCoreApplication.translate('PluginSyncQGISGeoServer', message)

    def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True, add_to_toolbar=True, status_tip=None, whats_this=None, parent=None):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)  # Agregar a la barra de herramientas

        if add_to_menu:
            self.iface.addPluginToMenu(self.tr(u'&SyncQGISGeoServer'), action)

        self.actions.append(action)

        return action

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, 'icon.png')  # Asegúrate de que 'icon.png' esté en la carpeta del plugin
        action = self.add_action(icon_path, text=self.tr(u'Sync QGIS with GeoServer'), callback=self.run, parent=self.iface.mainWindow())

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&SyncQGISGeoServer'), action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        auth_dialog = AuthenticationDialog()
        if auth_dialog.exec_():
            self.username = auth_dialog.get_username()
            self.password = auth_dialog.get_password()

            if not self.username or not self.password:
                QMessageBox.warning(None, "Error", "Username and password are required.")
                return

            if self.authenticate():
                self.show_main_dialog()
            else:
                QMessageBox.critical(None, "Error", "Authentication failed.")
        else:
            return

    def authenticate(self):
        # Implementa tu lógica de autenticación aquí
        # Por ejemplo, puedes usar las credenciales self.username y self.password
        # para realizar una solicitud a GeoServer u otro servicio de autenticación
        # y verificar las credenciales.
        # Devuelve True si la autenticación es exitosa, False si falla.
        # Aquí un ejemplo básico de autenticación:
        # Suponiendo que tu servicio de autenticación devuelve True o False
        # basado en si las credenciales son válidas.
        # Reemplaza este código con tu lógica de autenticación real.

        # Ejemplo básico de autenticación:
        if self.username == "admin" and self.password == "password":
            return True
        else:
            return False

    def show_main_dialog(self):
        dlg = PluginSyncQGISGeoServerDialog()
        dlg.exec_()

    def load_layers_from_geoserver(self):
        workspace = "geonode"  # Espacio de trabajo en GeoServer
        url = f"http://186.153.162.11:8085/geoserver/rest/workspaces/{workspace}/layers.json"

        try:
            response = requests.get(url, auth=(self.username, self.password))
            if response.status_code == 401:
                self.show_authentication_error()
                return

            response.raise_for_status()

            layers_info = response.json().get("layers", {}).get("layer", [])
            for layer_info in layers_info:
                layer_name = layer_info["name"]
                self.dlg.list_layers_geoserver.addItem(layer_name)  # Agregar el nombre de la capa a la lista en el diálogo
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener capas de GeoServer: {e}")

    def load_layers_from_qgis(self):
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            layer_name = layer.name()
            self.dlg.list_layers_qgis.addItem(layer_name)

    def show_authentication_error(self):
        QMessageBox.warning(self.dlg, "Authentication Error", "There was a problem with authentication. Please check your username and password and try again.")

    def import_layers_from_geoserver(self, layers_to_import, username, password):
        workspace = "geonode"  # Espacio de trabajo en GeoServer

        for layer_name in layers_to_import:
            uri = f"http://186.153.162.11:8085/geoserver/ows?service=wfs&version=1.0.0&request=GetFeature&typeName={layer_name}"

            layer = QgsVectorLayer(uri, layer_name, "WFS")
            if not layer.isValid():
                print(f"Error al cargar la capa {layer_name}")
            else:
                QgsProject.instance().addMapLayer(layer)
                print(f"Capa {layer_name} cargada exitosamente en QGIS")

    def export_layers_to_geoserver(self, layers_to_export, username, password):
        workspace = "geonode"
        data_store = "my_geonode_data"

        for layer_name in layers_to_export:
            temp_shapefile = os.path.join(self.plugin_dir, f"{layer_name}.zip")
            self.export_layer_to_shapefile(layer_name, temp_shapefile)
            self.upload_shapefile_to_geoserver(temp_shapefile, layer_name, workspace, data_store, username, password)
            self.publish_layer_in_geoserver(layer_name, workspace, data_store, username, password)
            os.remove(temp_shapefile)

    def export_layer_to_shapefile(self, layer_name, output_path):
        layer = QgsProject.instance().mapLayersByName(layer_name)[0]
        QgsVectorFileWriter.writeAsVectorFormat(layer, output_path, "utf-8", layer.crs(), "ESRI Shapefile")

    def upload_shapefile_to_geoserver(self, shapefile_path, layer_name, workspace, data_store, username, password):
        url = f"http://186.153.162.11:8085/geoserver/rest/workspaces/{workspace}/datastores/{data_store}/file.shp"
        with open(shapefile_path, 'rb') as file:
            response = requests.put(url, headers={'Content-type': 'application/zip'}, auth=(username, password), data=file)
            if response.status_code == 401:
                self.show_authentication_error()
                return

            if response.status_code == 201:
                print("Archivo subido exitosamente a GeoServer")
            else:
                print(f"Error al subir archivo a GeoServer: {response.status_code}")

    def publish_layer_in_geoserver(self, layer_name, workspace, data_store, username, password):
        url = f"http://186.153.162.11:8085/geoserver/rest/workspaces/{workspace}/datastores/{data_store}/featuretypes"
        data = f"<featureType><name>{layer_name}</name></featureType>"
        response = requests.post(url, headers={'Content-type': 'text/xml'}, auth=(username, password), data=data)
        if response.status_code == 401:
            self.show_authentication_error()
            return

        if response.status_code == 201:
            print("Capa publicada exitosamente en GeoServer")
        else:
            print(f"Error al publicar capa en GeoServer: {response.status_code}")         