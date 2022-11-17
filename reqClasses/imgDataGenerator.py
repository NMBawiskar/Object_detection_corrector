from json import load
import os
from symbol import return_stmt
from timeit import repeat

import cv2
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QInputDialog, QMainWindow, QStackedWidget, QWidget, QProgressBar, QDialog
import utils_pyqt5 as ut
from PyQt5.uic import loadUi
import random
from reqClasses.annotation_generator import AnnotationGenerator 
class RandomBGApplier(QWidget):
    def __init__(self):
        super().__init__()
        self.bgImgFolder = ""
        self.maskFullImgFolder = ""
       
        loadUi(r'uiFIles\randomBackgroundImgWindow.ui',self)


        self.listMaskImgs = []
        self.listPartImgs = []
        self.listBGImgs = []
        self.croppedPartImgFolder = ""

        self.output_folder = ""
        self.annotationGenerator = AnnotationGenerator()
        self.objectLabel = "Aluminium_plate"

        ####################### Generation parameters
        self.small_obj = True
        self.multiple_obj_per_bg_img = True
        self.maxcountMultiple_obj_per_bg_img = 3
        self.n_images_to_generate = 150
        self.multiple_copies_of_bg = False


        self.btn_browse_fullImgmask_folder.clicked.connect(self.browse_fullImg_mask_folder)
        self.btn_browse_mask_folder.clicked.connect(self.browse_mask_folder)
        self.btn_browse_bg_folder.clicked.connect(self.browse_BGImg_folder)
        self.btn_randomBgImgs.clicked.connect(self.generateRandomBGImages)
        self.btn_cropOutEachPart.clicked.connect(self.crop_each_part_and_save)


    def browse_fullImg_mask_folder(self):
        qWid = QWidget()
        print("file browse")
        path_folder = QFileDialog.getExistingDirectory(qWid, 'Select full image mask img folder', '')  
        self.textedit_fullImg_maskImgFolder.setPlainText("")      
        self.textedit_fullImg_maskImgFolder.setPlainText(path_folder)
        self.maskFullImgFolder = path_folder
       

    def browse_mask_folder(self):
        qWid = QWidget()
        print("file browse")
        path_folder = QFileDialog.getExistingDirectory(qWid, 'Select Cropped part masks img folder', '')  
        self.textedit_maskImgFolder.setPlainText("")      
        self.textedit_maskImgFolder.setPlainText(path_folder)
        self.croppedPartImgFolder = path_folder
        

    def browse_BGImg_folder(self):
        qWid = QWidget()
        print("file browse")
        path_folder = QFileDialog.getExistingDirectory(qWid, 'Select background img folder', '')  
        self.textedit_bgImgFolder.setPlainText("")      
        self.textedit_bgImgFolder.setPlainText(path_folder)
        self.bgImgFolder = path_folder


    def crop_each_part_and_save(self):
        self.__create_cropped_imgFolder()
        self.__getForeGroundImagesAndMasks(self.maskFullImgFolder)
        for i in range(len(self.listMaskImgs)):    
            maskImgFile = self.listMaskImgs[i]
            imgFile = self.listPartImgs[i]
            maskImgFilePath = os.path.join(self.maskFullImgFolder, maskImgFile)
            imgFilePath = os.path.join(self.maskFullImgFolder, imgFile)

            maskImg, foreGrImg = cv2.imread(maskImgFilePath), cv2.imread(imgFilePath)
            print("Seperating each part from mask..........")
        
            self.__generate_part_cropped_mask_imgs(maskImg=maskImg, orgImg=foreGrImg, fileName=imgFile)
            


    def setRandomBGImgFolderPath(self, bgImgFolderPath):
        if os.path.exists(bgImgFolderPath): 
            self.bgImgFolder = bgImgFolderPath
        else:
            print('Background image folder path does not exist!!. Please provide correct path...')


    def __getForeGroundImagesAndMasks(self, folder_to_Check):
        """self.maskFullImgFolder contains image and their mask with name _mask added at last of image name
        Checking masks if present adding to list"""
        allImgs = os.listdir(folder_to_Check)
        self.listMaskImgs = [fileName for fileName in allImgs if "_mask" in fileName]
        self.listPartImgs = [fileName.replace("_mask","") for fileName in self.listMaskImgs]

    def __generate_part_cropped_mask_imgs(self,  maskImg, orgImg, fileName):
        """Function cropped part of mask img and org img to a folder
        Params : maskImg : maskImg of part
        orgImg : corresponding color / gray img
        filename : fileName of img
        returns : saves the images to self.cropped_part_images"""

        singleChMask = maskImg[:,:,0]
        contours, heirarchy = cv2.findContours(singleChMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        
        if "." in fileName:
            fileNameWoExt = fileName.split(".")[0]
        else:
            fileNameWoExt = fileName

        for i, cnt in enumerate(contours):
            x,y,w,h = cv2.boundingRect(cnt)
            cropped_mask = maskImg[y:y+h, x:x+w]
            cropped_img = orgImg[y:y+h, x:x+w]
            area = cv2.contourArea(cnt)
            if area > 25:
                filePathCropped = os.path.join(self.croppedPartImgFolder, f"{fileNameWoExt}_{i}.png") 
                filePathMaskCropped = os.path.join(self.croppedPartImgFolder, f"{fileNameWoExt}_{i}_mask.png") 
                cv2.imwrite(filePathCropped, cropped_img)
                cv2.imwrite(filePathMaskCropped, cropped_mask)
        

    
    def __create_cropped_imgFolder(self):
        if len(self.maskFullImgFolder) >0 and os.path.exists(self.maskFullImgFolder):
            croppedPartImgFolder = "croppedMaskImgs"
            croppedPartImgFolderPath = os.path.join(self.maskFullImgFolder, croppedPartImgFolder)
            ut.create_directory(croppedPartImgFolderPath)
            self.croppedPartImgFolder = croppedPartImgFolderPath
        else:
            print("Problem in creating crooped Image folder")
    
    def __create_generated_img_n_annotations_folder(self):
        if len(self.croppedPartImgFolder) >0 and os.path.exists(self.croppedPartImgFolder):
            outputImageFolder = "random_generated_dataset"
            path_ = self.croppedPartImgFolder
            self.output_folder = path_.replace('croppedMaskImgs', outputImageFolder)            
            ut.create_directory(self.output_folder)

            
           
        else:
            print("Problem in creating crooped Image folder")


    def checkInputs(self):
        if self.textEdit_nImgToGenerate.toPlainText().strip().isnumeric():
            self.n_images_to_generate = int(self.textEdit_nImgToGenerate.toPlainText().strip())
            print("Ok n_inputs", self.n_images_to_generate)
        else:
            ut.showdialog("Please provide input digits only")
            return False

        if self.textEdit_nMaxPartsPerImg.toPlainText().strip().isnumeric():
            self.maxcountMultiple_obj_per_bg_img = int(self.textEdit_nMaxPartsPerImg.toPlainText().strip())
            print("Number of parts per image", self.maxcountMultiple_obj_per_bg_img)
        else:
            ut.showdialog("Please provide input digits only")
            return False

        if not os.path.exists(self.bgImgFolder):
            ut.showdialog("Please input Background images folder path")
            return False
        if not os.path.exists(self.croppedPartImgFolder):
            ut.showdialog("Please input cropped part images folder path")
            return False
        
        return True


    def generateRandomBGImages(self, k_random_bg_samples=2):
        """Function selects random background image and apply to the mask and part/object image (as foreground)"""
        
        if not self.checkInputs():
            ut.showdialog("Please provide proper inputs")
            return

            

        self.__getForeGroundImagesAndMasks(self.croppedPartImgFolder)   ## Part mask images and color images
        self.__create_generated_img_n_annotations_folder()
        print("Generating random imgs....")

        allowedImgExtensions = ['jpg', 'jpeg','png','bmp']
        bgfiles = os.listdir(self.bgImgFolder)

        self.listBGImgs = [file for file in bgfiles if file.split(".")[-1] in allowedImgExtensions]
        print('bg file list',self.listBGImgs)

        ############# Write logic of getting k random samples wrt to available BG images ##########################
        
        if self.n_images_to_generate <= len(self.listBGImgs):
            randomChosenImages = random.sample(self.listBGImgs,k=self.n_images_to_generate)

        else:
            factor = self.n_images_to_generate // len(self.listBGImgs)
            factor+=1
            randomChosenImages_list = []
            for i in range(factor):
                randomChosenImages_list.extend(self.listBGImgs)
            
            randomChosenImages = randomChosenImages_list[:self.n_images_to_generate]
            random.shuffle(randomChosenImages)

        for file in randomChosenImages:
            try:
                filePath = os.path.join(self.bgImgFolder, file)
                bgImg = cv2.imread(filePath)
                obj_xywh_list_to_parse = []
                hImg,wImg,chImg = bgImg.shape 
                    

                ### Select random part img and mask
                if self.multiple_obj_per_bg_img:
                    randomCntObj = random.randint(1, self.maxcountMultiple_obj_per_bg_img)
                    selected_index_list = []
                    for i in range(randomCntObj):
                        # print(self.listMaskImgs)
                        randomIndex = random.randint(0, len(self.listMaskImgs)//2)
                        selected_index_list.append(randomIndex)

                    result_img, obj_xywh_list = self.__create_bg_img_with_multiple_parts_n_annotations(selectedbgImg=bgImg,
                                                selectedPartImgIndices=selected_index_list)

                    bgImgName_wo_ext = file.split(".")[0]
                    outputImgFileName = f"{bgImgName_wo_ext}_1.png"
                    path_output = os.path.join(self.output_folder, outputImgFileName)
                    cv2.imwrite(path_output, result_img)

                    # annotated_display_img = self.__check_annotation(result_img,obj_xywh_list)
                    outputAnnotatedImgFileName =  f"{bgImgName_wo_ext}_1_annotated.png"
                    path_output_annotated = os.path.join(self.output_folder,outputImgFileName)
                    # cv2.imwrite(path_output_annotated, annotated_display_img)

                    #################################### Create annotation file ##############################
                    
                    for x_,y_,w_,h_ in obj_xywh_list:
                        temp_list = [self.objectLabel, x_,y_,x_+w_,y_+h_]
                        obj_xywh_list_to_parse.append(temp_list)

                    self.annotationGenerator.objectName_xyxy_list = obj_xywh_list_to_parse                
                    imgPath_for_annotation = os.path.join(self.output_folder, outputImgFileName)
            
                    self.annotationGenerator.create_annotation(self.output_folder,outputImgFileName, 
                            imgPath_for_annotation, w_img=wImg, h_img=hImg, ch_img=chImg)
            except Exception as e:
                print("Error",e)

        ut.showdialog(f"Done. Generated {len(randomChosenImages)} synthetic image with annotations ")

                


    def __create_bg_img_with_multiple_parts_n_annotations(self,selectedbgImg, selectedPartImgIndices:list):
        hBGImg, wBGImg = selectedbgImg.shape[:2]
        # print("selectedPartImgIndices",selectedPartImgIndices)
        fgMaskReq = np.zeros((hBGImg,wBGImg,1), np.uint8) # 1 channel mask image on which part white mask crops will be added
        fgImgReq = np.ones((hBGImg,wBGImg,3), np.uint8) # 3 channel white image on which part color crops will be added
        obj_xywh_list = []
        result_added = selectedbgImg.copy()
        for index in selectedPartImgIndices:
            maskImgFile = self.listMaskImgs[index]
            imgFile = self.listPartImgs[index]
            maskImgFilePath = os.path.join(self.croppedPartImgFolder, maskImgFile)
            imgFilePath = os.path.join(self.croppedPartImgFolder, imgFile)
            partMaskImg, partFGImg = cv2.imread(maskImgFilePath), cv2.imread(imgFilePath)
            hPart, wPart = partMaskImg.shape[:2]
            
            ##### Place on random location the part
            x_random = random.randint(0, wBGImg- wPart-2)
            y_random = random.randint(0, hBGImg- hPart-2)
            x1, y1 ,x2, y2 = x_random, y_random, x_random+wPart, y_random+hPart
            obj_xywh = [x1,y1,wPart, hPart]
            obj_xywh_list.append(obj_xywh)
            partMaskImg = partMaskImg[:,:,0]
            partMaskImg = np.expand_dims(partMaskImg, axis=2)
            fgMaskReq[y1:y2, x1:x2] = partMaskImg
            fgImgReq[y1:y2, x1:x2] = partFGImg
        
            result_added = self.__applyBGToPartImg(result_added, fgImg= fgImgReq, maskImg = fgMaskReq)
        
        return [result_added, obj_xywh_list]


    def __applyBGToPartImg(self, bgImg, fgImg, maskImg):
        bgH, bgW = bgImg.shape[:2]
        fgH, fgW = fgImg.shape[:2]
        maskH, maskW, maskCh = maskImg.shape
        mask1Ch = maskImg[:,:,0]
        maskImg = mask1Ch
        
        if bgH!=fgH or bgW!=fgW:
            bgImg = cv2.resize(bgImg, (fgW, fgH), interpolation=cv2.INTER_AREA)
        maskImgNot = cv2.bitwise_not(maskImg)

        fr = cv2.bitwise_and(fgImg, fgImg, mask=maskImg)
        bg = cv2.bitwise_and(bgImg, bgImg, mask= maskImgNot)
        added = fr+ bg

        return added

    def __check_annotation(self, img, list_obj_xywh):
        for x,y,w,h in list_obj_xywh:
            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0),2)
        return img

