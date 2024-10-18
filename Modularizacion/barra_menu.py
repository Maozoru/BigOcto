from PyQt6.QtWidgets import QMenuBar, QFileDialog, QMessageBox
from PyQt6.QtGui import QAction
import numpy as np

class BarraMenu(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Crear un menú "Archivo"
        archivo_menu = self.addMenu("Archivo")
        
        # Acciones del menú
        nuevo_action = QAction("Nuevo", self)
        abrir_action = QAction("Abrir", self)
        guardar_action = QAction("Guardar como...", self)
        salir_action = QAction("Salir", self)

        # Conectar las acciones a métodos
        nuevo_action.triggered.connect(self.nuevo_archivo)
        abrir_action.triggered.connect(self.abrir_archivo)
        guardar_action.triggered.connect(self.mostrar_menu_guardar)
        salir_action.triggered.connect(parent.close)

        # Agregar acciones al menú
        archivo_menu.addAction(nuevo_action)
        archivo_menu.addAction(abrir_action)
        archivo_menu.addAction(guardar_action)
        archivo_menu.addSeparator()
        archivo_menu.addAction(salir_action)

    def nuevo_archivo(self):
        # Lógica para crear un nuevo archivo
        QMessageBox.information(self.parent(), "Nuevo Archivo", "Se ha creado un nuevo archivo.")

    def abrir_archivo(self):
        # Lógica para abrir un archivo
        opciones = QFileDialog.Options()
        archivo, _ = QFileDialog.getOpenFileName(self.parent(), "Abrir Archivo", "", "Todos los Archivos (*);;Archivos de Texto (*.txt)", options=opciones)
        if archivo:
            QMessageBox.information(self.parent(), "Archivo Abierto", f"Se ha abierto el archivo: {archivo}")

    def mostrar_menu_guardar(self):
        # Método para mostrar el menú de guardar
        ruta, _ = QFileDialog.getSaveFileName(self.parent(), "Guardar archivo", "", "Imagen PNG (*.png);;Imagen JPG (*.jpg)")
        if ruta:
            formato = "PNG" if ruta.endswith(".png") else "JPG"
            # Asegúrate de que el método guardar_lienzo esté implementado en la clase padre
            if hasattr(self.parent(), 'guardar_lienzo'):
                self.parent().guardar_lienzo(ruta, formato)
            else:
                QMessageBox.warning(self.parent(), "Error", "Método guardar_lienzo no encontrado en el lienzo de dibujo.")

