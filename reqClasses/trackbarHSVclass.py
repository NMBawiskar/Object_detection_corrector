import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QInputDialog, QMainWindow, QStackedWidget, QWidget, QProgressBar, QDialog
import utils_pyqt5 as ut
from PyQt5.uic import loadUi
import os
import utils_pyqt5 as ut
import numpy as np
from PIL import Image
from PIL.ImageQt import ImageQt

class HSVThresholder(QWidget):
    def __init__(self, objImgDataset):
        super().__init__()
        self.imgPath = None
        self.objImgDataset = objImgDataset
                     
        loadUi(r'uiFIles\trackBarHSV.ui',self)

        self.imgToshow = None

        self.slider_hmin.valueChanged.connect(self.sliderHMinChanged)
        self.slider_hmax.valueChanged.connect(self.sliderHMaxChanged)
        self.slider_smin.valueChanged.connect(self.sliderSMinChanged)
        self.slider_smax.valueChanged.connect(self.sliderSMaxChanged)
        self.slider_vmin.valueChanged.connect(self.sliderVMinChanged)
        self.slider_vmax.valueChanged.connect(self.sliderVMaxChanged)

        self.btn_prev_img.clicked.connect(self.show_prevImg)
        self.btn_next_img.clicked.connect(self.show_nextImg)
        self.btn_first_img.clicked.connect(self.show_firstImg)
        self.btn_last_img.clicked.connect(self.show_lastImg)

        self.btn_save_masks.clicked.connect(self.saveMasks)
        self.hmin = 0
        self.hmax = 179
        self.vmin = 0
        self.vmax = 255
        self.smin =0
        self.smax = 255
        self.imgPathToShow = ""
        self.getImgToShow()
        self.currentImgIndex = 0

    def getImgToShow(self):
        self.currentImgIndex = self.objImgDataset.currentImgIndex
        self.imgNameToShow = self.objImgDataset.imageFileNameList[self.currentImgIndex]
        self.imgPathToShow = os.path.join(self.objImgDataset.imgDirPath, self.imgNameToShow)
        self.apply_hsv_threshold()

    def showImgThreshold(self):
        self.imgNameToShow = self.objImgDataset.imageFileNameList[self.currentImgIndex]
        self.imgPathToShow = os.path.join(self.objImgDataset.imgDirPath, self.imgNameToShow)
        self.apply_hsv_threshold()

    def sliderHMinChanged(self):
        self.hmin = self.slider_hmin.value()
        self.label_hminVal.setText(str(self.hmin))
        self.apply_hsv_threshold()

    def sliderHMaxChanged(self):
        self.hmax = self.slider_hmax.value()
        self.label_hmaxVal.setText(str(self.hmax))
        self.apply_hsv_threshold()
    def sliderSMinChanged(self):
        self.smin = self.slider_smin.value()
        self.label_sminVal.setText(str(self.smin))
        self.apply_hsv_threshold()

    def sliderSMaxChanged(self):
        self.smax = self.slider_smax.value()
        self.label_smaxVal.setText(str(self.smax))
        self.apply_hsv_threshold()

    def sliderVMinChanged(self):
        self.vmin = self.slider_vmin.value()
        self.label_vminVal.setText(str(self.vmin))
        self.apply_hsv_threshold()

    def sliderVMaxChanged(self):
        self.vmax = self.slider_vmax.value()
        self.label_vmaxVal.setText(str(self.vmax))
        self.apply_hsv_threshold()

    def show_lastImg(self):
        self.currentImgIndex = len(self.objImgDataset.imageFileNameList)-1
        self.showImgThreshold()
    
    def show_firstImg(self):
        self.currentImgIndex =0 
        self.showImgThreshold()
    
    


    def show_prevImg(self):
        if self.currentImgIndex>0:
            self.currentImgIndex -=1
            self.showImgThreshold()

    def show_nextImg(self):
        if self.currentImgIndex<len(self.objImgDataset.imageFileNameList)-1:
            self.currentImgIndex +=1
            self.showImgThreshold()

    def get_1_ch_hsv_mask(self,img):        
        imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lowerLimit = np.array([self.hmin, self.smin, self.vmin])
        upperLimit = np.array([self.hmax,self.smax, self.vmax])
        imgMask = cv2.inRange(imgHSV, lowerLimit, upperLimit)
        return imgMask


    def apply_hsv_threshold(self):
        img = cv2.imread(self.imgPathToShow)
        imgMask = self.get_1_ch_hsv_mask(img)
      
        mask3Ch = cv2.merge((imgMask, imgMask,imgMask))

        imgToshow = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        hstack = np.hstack((imgToshow, mask3Ch))
        imgPil = Image.fromarray(hstack)
        im = ImageQt(imgPil).copy()
        pixmap = QtGui.QPixmap.fromImage(im)
        self.label_hsvImgDisplay.setPixmap(pixmap)
        self.label_cnt.setText(f"{self.currentImgIndex+1}/{len(self.objImgDataset.imageFileNameList)}")

    def saveMasks(self):
        for imgFile in self.objImgDataset.imageFileNameList:
            imgPath = os.path.join(self.objImgDataset.imgDirPath, imgFile)
            img = cv2.imread(imgPath)

            maskHSV = self.get_1_ch_hsv_mask(img)
            mask3Ch = cv2.merge((maskHSV, maskHSV,maskHSV))

            maskImgName = imgFile.split(".")[0] + "_mask.png"
            maskImgPath = os.path.join(self.objImgDataset.imgDirPath, maskImgName)
            cv2.imwrite(maskImgPath, mask3Ch)
            
        ut.showdialog("All HSV masks saved successfully!!")
