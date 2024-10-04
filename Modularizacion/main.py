import sys
from PyQt6.QtWidgets import QApplication
from lienzo_de_dibujo import LienzoDeDibujo

def main():
    app = QApplication(sys.argv)
    ventana = LienzoDeDibujo()
    ventana.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
