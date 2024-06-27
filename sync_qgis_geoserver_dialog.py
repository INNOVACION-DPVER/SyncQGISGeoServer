# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PluginSyncQGISGeoServerDialog
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
from qgis.PyQt.QtWidgets import QDialog, QListWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QCheckBox, QMessageBox

class AuthenticationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Authentication")

        self.lbl_username = QLabel("Username:")
        self.lbl_password = QLabel("Password:")
        self.txt_username = QLineEdit()
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.chk_remember = QCheckBox("Remember credentials")

        self.btn_login = QPushButton("Login")
        self.btn_login.clicked.connect(self.login_clicked)

        layout = QVBoxLayout()
        layout.addWidget(self.lbl_username)
        layout.addWidget(self.txt_username)
        layout.addWidget(self.lbl_password)
        layout.addWidget(self.txt_password)
        layout.addWidget(self.chk_remember)
        layout.addWidget(self.btn_login)

        self.setLayout(layout)

    def login_clicked(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Username and password are required.")
            return

        self.accept()

    def get_username(self):
        return self.txt_username.text()

    def get_password(self):
        return self.txt_password.text()


class PluginSyncQGISGeoServerDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sync QGIS with GeoServer")

        # Lista de layers disponibles en GeoServer para importar
        self.list_layers_geoserver = QListWidget()
        self.list_layers_geoserver.setSelectionMode(QListWidget.MultiSelection)

        # Lista de layers seleccionados para exportar desde QGIS a GeoServer
        self.list_layers_qgis = QListWidget()
        self.list_layers_qgis.setSelectionMode(QListWidget.MultiSelection)

        # Botones para agregar y quitar layers
        self.btn_add_to_qgis = QPushButton("Add to QGIS")
        self.btn_remove_from_qgis = QPushButton("Remove from QGIS")
        self.btn_import_from_geoserver = QPushButton("Import from GeoServer")
        self.btn_export_to_geoserver = QPushButton("Export to GeoServer")

        layout_layers = QVBoxLayout()
        layout_layers.addWidget(self.list_layers_geoserver)
        layout_layers.addWidget(self.btn_import_from_geoserver)
        layout_layers.addWidget(self.btn_export_to_geoserver)
        layout_layers.addWidget(self.list_layers_qgis)
        layout_layers.addWidget(self.btn_add_to_qgis)
        layout_layers.addWidget(self.btn_remove_from_qgis)

        self.setLayout(layout_layers)

    def selected_layers_to_export(self):
        selected_layers = []
        for item in self.list_layers_qgis.selectedItems():
            selected_layers.append(item.text())
        return selected_layers

    def selected_layers_to_import(self):
        selected_layers = []
        for item in self.list_layers_geoserver.selectedItems():
            selected_layers.append(item.text())
        return selected_layers