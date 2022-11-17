import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QInputDialog, QMainWindow, QStackedWidget, QWidget, QProgressBar, QDialog
import utils_pyqt5 as ut
from PyQt5.uic import loadUi
import os
import utils_pyqt5 as ut
from reqClasses.trackbarHSVclass import HSVThresholder
from reqClasses.painterClass import PaintImg

class SynthImgAugmentor(QWidget):
    def __init__(self):
        super().__init__()
        self.imgPath = None
                     
        loadUi(r'uiFIles\form_synthetic.ui',self)

        self.imgDirPath = ""
        self.imageFileNameList = []
        self.currentImgIndex = 0
        self.firstImgPath = ""
        self.firstImg = None
        self.currentImg = None
        
        ################ Actions #################
        self.btn_edit_masks.clicked.connect(self.to_edit_mask)
        self.btn_browse_img.clicked.connect(self.browse_img_file)
        self.btn_browse_img_folder.clicked.connect(self.browse_folder)
        self.btn_prev_img.clicked.connect(self.show_prevImg)
        self.btn_next_img.clicked.connect(self.show_nextImg)
        self.btn_first_img.clicked.connect(self.show_firstImg)
        self.btn_last_img.clicked.connect(self.show_lastImg)

        self.btn_set_color_threshold.clicked.connect(self.to_hsv_threshold)
        
    def to_hsv_threshold(self):
        if len(self.imageFileNameList)>0:
            hsvThresholder = HSVThresholder(self)
            self.window= hsvThresholder
            self.window.show()
        else:
            ut.showdialog("Please select image or folder first !!")
    
    def show_lastImg(self):
        self.currentImgIndex = len(self.imageFileNameList)-1
        self.show_current_img()
    
    def show_firstImg(self):
        self.currentImgIndex =0 
        self.show_current_img()
    
    
    def to_edit_mask(self):
        self.editMaskScreen = PaintImg(self)
        self.window = self.editMaskScreen
        self.window.show()
       


    def show_prevImg(self):
        if self.currentImgIndex>0:
            self.currentImgIndex -=1
            self.show_current_img()

    def show_nextImg(self):
        if self.currentImgIndex<len(self.imageFileNameList)-1:
            self.currentImgIndex +=1
            self.show_current_img()


    def setImgPath(self, imgpath):
        self.imgPath = imgpath
    
    
    def browse_img_file(self):

        qWid = QWidget()
        print("file browse")
        path,_ = QFileDialog.getOpenFileName(qWid, 'Open a image', '','Image Files (*.*)')        
        self.image_path_textedit.setPlainText(path)
        self.image_folder_path_textedit.setPlainText("")
        self.imageFileNameList= []
        fileName = os.path.basename(path)
        dir = os.path.dirname(path)
        self.imageFileNameList.append(fileName)
        self.imgDirPath =dir
        self.currentImgIndex =0 
        if len(path)>0:
            self.show_current_img()

    def browse_folder(self):
        qWid = QWidget()
        print("file browse")
        path_folder = QFileDialog.getExistingDirectory(qWid, 'Select folder', '')  
        self.image_path_textedit.setPlainText("")      
        self.image_folder_path_textedit.setPlainText(path_folder)
        self.imgDirPath = path_folder
        if len(path_folder)>0:
            self.list_images()
    
    def list_images(self):
        files = os.listdir(self.imgDirPath)
        imageExtensions = ['bmp','jpg','jpeg','png','tiff']
        self.imageFileNameList = [fileName for fileName in files if fileName.split(".")[-1] in imageExtensions]
        self.imageFileNameList = [fileName for fileName in self.imageFileNameList if "_mask" not in fileName]
        if len(self.imageFileNameList)>0:
            firstImgName = self.imageFileNameList[0]    
            firstImgPath = os.path.join(self.imgDirPath, firstImgName)
            ut.apply_img_to_label_object(firstImgPath, self.label_image_display)

    def show_current_img(self):
        currentImgpath = os.path.join(self.imgDirPath, self.imageFileNameList[self.currentImgIndex])
        ut.apply_img_to_label_object(currentImgpath, self.label_image_display)
        self.label_cnt.setText(f"{self.currentImgIndex+1}/{len(self.imageFileNameList)}")