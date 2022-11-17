from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QInputDialog, QWidget, QProgressBar
import os


from PIL import Image
from PIL.ImageQt import ImageQt


# browse directory

def browse_output_directory(self):

    qWid = QWidget()
    print("file browse")
    path = QFileDialog.getExistingDirectory(qWid, 'Select Folder')        
    self.textEdit_save_dir.setPlainText(path)
 



## add image on the label 

def add_image(self, imgPath, uiObject):
        self.uiObject = uiObject        
        Image.MAX_IMAGE_PIXELS = 933120000   ## This is for very big images
        imgPIL = Image.open(imgPath)        
        size = imgPIL.size
        imgPIL = imgPIL.resize((1280,720))
        im = ImageQt(imgPIL).copy()
        
        self.pixmap = QtGui.QPixmap.fromImage(im)
        self.label.setPixmap(self.pixmap)


def update_list_widget(self):
    self.img_list = []
    self.img_path_list = []
    self.img_list = os.listdir(self.identified_peoples_dir_path)
    self.img_path_list = [os.path.join(self.identified_peoples_dir_path, filename) for filename in self.img_list]

    #create QIcon
    # icon = QtGui.QIcon('img\arrow_left.png')
    # reverse_list =  self.img_path_list[-10:]
    self.listWidget.clear()
    reverse_list = self.img_path_list[::-1]
    for imgPath in reverse_list:
        # imgfile = img
        # imgPath = os.path.join(self.identified_peoples_dir_path, imgfile)

        imgPil = Image.open(imgPath)
        # im_resized = imgPil.resize((300,100))    
        im = ImageQt(imgPil).copy()
        pixmap = QtGui.QPixmap.fromImage(im)
        icon = QtGui.QIcon(pixmap)
        # size = QtCore.QSize()
        # size.setHeight(100)
        # size.setWidth(400)
        item = QtWidgets.QListWidgetItem()
        self.listWidget.setIconSize(QtCore.QSize(330, 250))
        # item.setSizeHint(size)
        item.setIcon(icon)
        self.listWidget.addItem(item)

