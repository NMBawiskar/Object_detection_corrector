from PyQt5 import QtWidgets, QtMultimedia, QtCore,QtGui
from PyQt5.QtGui import QImage, QPixmap
import sys
import utils_pyqt5 as ut
from PyQt5.uic import loadUi


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
             
        loadUi(r'uiFiles\mainUi.ui',self)
        
        
        self.btnDebug.clicked.connect(self.debug_start)
       
        

    def is_valid(self):
        if self.textEdit_fileNames.toPlainText() != '':
            return True
        else:
            return False

       
       
    def debug_start(self):
        self.label.clear()
        self.textEdit.clear()
        self.label.setText("Please enter the employee name.") 
        self.resrt = True

 
          
    def displayImage(self, uiObj, img):
        qformat = QImage.Format_BGR888
        img = QImage(img, img.shape[1], img.shape[0], qformat)
        uiObj.setPixmap(QPixmap.fromImage(img))

    def close_win(self):
        self.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    w.setWindowTitle("Registration window")
    w.setWindowIcon(QtGui.QIcon(r'resources/QuicSolv-Fevicon.png'))
    sys.exit(app.exec())
    