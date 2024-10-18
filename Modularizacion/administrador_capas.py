from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QWidget, QListWidget, QInputDialog, QSlider
from PyQt6.QtCore import Qt

class AdministradorCapas(QWidget):
    """ Clase para administrar las capas del lienzo de dibujo. """
    
    def __init__(self, lienzo_dibujo):
        super().__init__()

        self.setWindowTitle("Administrador de Capas")
        self.setFixedSize(300, 400)

        self.lienzo_dibujo = lienzo_dibujo  # Referencia al lienzo principal

        # Layout de la ventana de capas
        self.diseno = QVBoxLayout(self)

        # Lista de capas
        self.lista_capas = QListWidget(self)
        self.diseno.addWidget(self.lista_capas)

        # Botones para manejar capas
        self.boton_nueva_capa = QPushButton("Nueva Capa", self)
        self.boton_nueva_capa.clicked.connect(self.crear_nueva_capa)
        self.diseno.addWidget(self.boton_nueva_capa)

        self.boton_eliminar_capa = QPushButton("Eliminar Capa", self)
        self.boton_eliminar_capa.clicked.connect(self.eliminar_capa_actual)
        self.diseno.addWidget(self.boton_eliminar_capa)

        self.boton_renombrar_capa = QPushButton("Renombrar Capa", self)
        self.boton_renombrar_capa.clicked.connect(self.renombrar_capa)
        self.diseno.addWidget(self.boton_renombrar_capa)

        self.boton_ocultar_capa = QPushButton("Ocultar Capa", self)
        self.boton_ocultar_capa.clicked.connect(self.ocultar_capa)
        self.diseno.addWidget(self.boton_ocultar_capa)

        self.boton_mostrar_capa = QPushButton("Mostrar Capa", self)
        self.boton_mostrar_capa.clicked.connect(self.mostrar_capa)
        self.diseno.addWidget(self.boton_mostrar_capa)

        self.boton_bloquear_capa = QPushButton("Bloquear Capa", self)
        self.boton_bloquear_capa.clicked.connect(self.bloquear_capa)
        self.diseno.addWidget(self.boton_bloquear_capa)

        self.boton_desbloquear_capa = QPushButton("Desbloquear Capa", self)
        self.boton_desbloquear_capa.clicked.connect(self.desbloquear_capa)
        self.diseno.addWidget(self.boton_desbloquear_capa)

        self.boton_fusionar_capa = QPushButton("Fusionar Capa", self)
        self.boton_fusionar_capa.clicked.connect(self.fusionar_capa)
        self.diseno.addWidget(self.boton_fusionar_capa)

        self.boton_clonar_capa = QPushButton("Clonar Capa", self)
        self.boton_clonar_capa.clicked.connect(self.clonar_capa)
        self.diseno.addWidget(self.boton_clonar_capa)

        self.boton_reorganizar_capas = QPushButton("Reorganizar Capas", self)
        self.boton_reorganizar_capas.clicked.connect(self.reorganizar_capas)
        self.diseno.addWidget(self.boton_reorganizar_capas)

        # Control deslizante para opacidad
        self.control_deslizante_opacidad = QSlider(Qt.Orientation.Horizontal, self)
        self.control_deslizante_opacidad.setRange(0, 100)
        self.control_deslizante_opacidad.valueChanged.connect(self.ajustar_opacidad)
        self.diseno.addWidget(self.control_deslizante_opacidad)

        # Sincronizar la lista de capas con las capas del lienzo
        self.actualizar_lista_capas()

    def crear_nueva_capa(self):
        """ Crea una nueva capa en el lienzo. """
        self.lienzo_dibujo.crear_nueva_capa()  # Afecta al lienzo
        self.actualizar_lista_capas()  # Actualiza la lista de capas en la interfaz

    def eliminar_capa_actual(self):
        """ Elimina la capa actual en el lienzo. """
        fila_actual = self.lista_capas.currentRow()
        if fila_actual != -1:
            self.lienzo_dibujo.eliminar_capa(fila_actual)  # Elimina la capa en el lienzo
            self.actualizar_lista_capas()  # Actualiza la lista de capas
            self.lienzo_dibujo.update_canvas()  # Asegúrate de actualizar el lienzo

    def renombrar_capa(self):
        fila_actual = self.lista_capas.currentRow()
        if fila_actual != -1:
            nuevo_nombre, ok = QInputDialog.getText(self, "Renombrar capa", "Ingrese el nuevo nombre de la capa")
            if ok and nuevo_nombre:
                self.lienzo_dibujo.capas[fila_actual].renombrar(nuevo_nombre)
                self.actualizar_lista_capas()

    def ocultar_capa(self):
        """ Oculta la capa seleccionada. """
        fila_actual = self.lista_capas.currentRow()
        if fila_actual != -1:
            self.lienzo_dibujo.ocultar_capa(fila_actual)  # Afecta al lienzo
            self.lienzo_dibujo.update_canvas()  # Actualiza el lienzo
            self.actualizar_lista_capas()  # Actualiza la lista

    def mostrar_capa(self):
        """ Muestra la capa seleccionada. """
        fila_actual = self.lista_capas.currentRow()
        if fila_actual != -1:
            self.lienzo_dibujo.mostrar_capa(fila_actual)  # Afecta al lienzo
            self.lienzo_dibujo.update_canvas()  # Actualiza el lienzo
            self.actualizar_lista_capas()  # Actualiza la lista

    def bloquear_capa(self):
        fila_actual = self.lista_capas.currentRow()
        if fila_actual != -1:
            self.lienzo_dibujo.bloquear_capa(fila_actual)

    def desbloquear_capa(self):
        fila_actual = self.lista_capas.currentRow()
        if fila_actual != -1:
            self.lienzo_dibujo.desbloquear_capa(fila_actual)

    def ajustar_opacidad(self):
        """ Ajusta la opacidad de la capa seleccionada. """
        fila_actual = self.lista_capas.currentRow()
        if fila_actual != -1:
            nueva_opacidad = self.control_deslizante_opacidad.value() / 100
            self.lienzo_dibujo.ajustar_opacidad(fila_actual, nueva_opacidad)

    def fusionar_capa(self):
        fila_actual = self.lista_capas.currentRow()
        if fila_actual != -1 and fila_actual > 0:
            # Fusiona la capa actual con la capa inferior
            self.lienzo_dibujo.fusionar_capas(fila_actual)
            self.actualizar_lista_capas()

    def clonar_capa(self):
        fila_actual = self.lista_capas.currentRow()
        if fila_actual != -1:
            # Clona la capa actual
            self.lienzo_dibujo.clonar_capa(fila_actual)
            self.actualizar_lista_capas()

    def reorganizar_capas(self):
        fila_actual = self.lista_capas.currentRow()
        if fila_actual != -1:
            # Mostrar un diálogo para seleccionar nueva posición
            nueva_posicion, ok = QInputDialog.getInt(self, "Reorganizar capas", 
                                                    "Nueva posición (0 para la capa superior)", 0, 0, len(self.lienzo_dibujo.capas) - 1)
            if ok and nueva_posicion != fila_actual:
                # Cambia 'reorganizar_capa' por 'reorganizar_capas'
                self.lienzo_dibujo.reorganizar_capas(fila_actual, nueva_posicion)
                self.actualizar_lista_capas()

    def actualizar_lista_capas(self):
        """ Actualiza la lista de capas con el estado actual del lienzo. """
        self.lista_capas.clear()
        for i, capa in enumerate(self.lienzo_dibujo.capas):
            visibilidad = " (Oculta)" if not capa.visible else ""
            self.lista_capas.addItem(f"Capa {i + 1}: {capa.name}{visibilidad}")
        self.lista_capas.setCurrentRow(self.lienzo_dibujo.indice_capa_actual)
        # Sincronizar opacidad de la capa seleccionada
        if self.lienzo_dibujo.indice_capa_actual != -1:
            opacidad_actual = self.lienzo_dibujo.capas[self.lienzo_dibujo.indice_capa_actual].opacidad
            self.control_deslizante_opacidad.setValue(int(opacidad_actual * 100))
