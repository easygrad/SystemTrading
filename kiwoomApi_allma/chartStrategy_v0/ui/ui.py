import sys
from PyQt5.QtWidgets import *
from kiwoom.kiwoom import *

class Ui():
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.kiwoom = Kiwoom()
        self.app.exec()