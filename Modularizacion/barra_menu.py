from PyQt6.QtWidgets import QMenuBar, QFileDialog, QMessageBox
from PyQt6.QtGui import QAction, QIcon

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

        # Crear menú de "Ver" para las acciones de Zoom
        ver_menu = self.addMenu("Ver")

        # Acción para Zoom In
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.triggered.connect(parent.zoom_in)
        ver_menu.addAction(zoom_in_action)

        # Acción para Zoom Out
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.triggered.connect(parent.zoom_out)
        ver_menu.addAction(zoom_out_action)

        # Crear menú "Editar"
        editar_menu = self.addMenu("Editar")

        # Crear acciones para Deshacer y Rehacer
        deshacer_action = QAction(QIcon("volver.png"), "Deshacer", self)
        # deshacer_action.triggered.connect(parent.deshacer)  # Conectar a la función de deshacer en LienzoDeDibujo

        rehacer_action = QAction(QIcon("rehacer.png"), "Rehacer", self)
        # rehacer_action.triggered.connect(parent.rehacer)  # Conectar a la función de rehacer en LienzoDeDibujo

        # Agregar acciones de Deshacer y Rehacer al menú "Editar"
        editar_menu.addAction(deshacer_action)
        editar_menu.addAction(rehacer_action)

        # Crear el menú de guardar
        self.crear_menu_guardar()

    def crear_menu_guardar(self):
        """ Crea el menú de guardar. """
        guardar_action = QAction("Guardar", self)
        guardar_action.triggered.connect(self.mostrar_menu_guardar)
        self.addAction(guardar_action)  # Agregar la acción al menú

    def nuevo_archivo(self):
        """ Lógica para crear un nuevo archivo. """
        QMessageBox.information(self.parent(), "Nuevo Archivo", "Se ha creado un nuevo archivo.")

    def abrir_archivo(self):
        """ Lógica para abrir un archivo. """
        opciones = QFileDialog.Options()
        archivo, _ = QFileDialog.getOpenFileName(self.parent(), "Abrir Archivo", "", "Todos los Archivos (*);;Archivos de Texto (*.txt)", options=opciones)
        if archivo:
            QMessageBox.information(self.parent(), "Archivo Abierto", f"Se ha abierto el archivo: {archivo}")

    def mostrar_menu_guardar(self):
        """ Muestra un diálogo para guardar el lienzo. """
        ruta, _ = QFileDialog.getSaveFileName(self.parent(), "Guardar Lienzo", "", "Imágenes PNG (*.png);;Imágenes JPG (*.jpg)")
        if ruta:  # Ver ifica que se haya seleccionado una ruta
            formato = "PNG" if ruta.endswith(".png") else "JPEG"
            self.parent().guardar_lienzo(ruta, formato)