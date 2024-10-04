from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton

class AdministradorCapas(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Administrador de Capas")
        self.setFixedSize(300, 400)
        self.layout = QVBoxLayout(self)

        self.lista_capas = QListWidget(self)
        self.layout.addWidget(self.lista_capas)

        self.boton_agregar = QPushButton("Agregar Capa", self)
        self.boton_agregar.clicked.connect(parent.crear_nueva_capa)
        self.layout.addWidget(self.boton_agregar)

        # ... más código para administrar capas ...

    def actualizar_lista_capas(self):
        self.lista_capas.clear()
        for capa in parent.capas:
            self.lista_capas.addItem(capa.nombre)
