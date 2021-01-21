from kiwoom.kiwoom_noti import *
from PyQt5.QtWidgets import *
import sys

class Ui_class():
    def __init__(self):
        print("Ui_class 입니다.")

        self.app = QApplication(sys.argv)
        self.kiwoom = Kiwoom()
        self.app.exec_()



    

