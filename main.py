from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from SRC.veikla_main import Window




if __name__ == "__main__":
    a = QtWidgets.QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(a.exec())