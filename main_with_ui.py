
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QInputDialog, QMainWindow, QStackedWidget, QWidget, QProgressBar, QDialog
from PyQt5.uic import loadUi
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
import os
import cv2
from PIL.ImageQt import ImageQt
from PIL import Image

from add_database import Add_Faces

from CamProcessor import Camera
from faceEncode_decoder import FaceEncodeDecoder
from global_settings import GlobalSettings
from reports_view import ReportsView
from view_database import ViewDB
from utils_pyqt5 import apply_img_to_label_object, showdialog, create_directory


class MyMainWindow(QMainWindow):
    def __init__(self, app):
        super(MyMainWindow, self).__init__()
        loadUi('dashboard_ui.ui',self)

        
        # #----------------- Variables -------------------------
        self.camObject = None
        self.faceDetectionObject = None

        self.settings_file_path = 'Settings.csv'
        self.streaming= False
        self.rtsp_link = ''
        self.n_jitters = 1
        self.detection_threshold = 0.55


        #--- directories all 
        self.main_dir = 'data_dir'
        self.recording_dir_path = r'recordings'

        self.trained_enc_directory_path = os.path.join(self.main_dir, 'Trained_encodings')
        self.known_persons_directory_path = os.path.join(self.main_dir, 'Known_person_images')
        self.Unknown_persons_directory_path = os.path.join(self.main_dir, 'Unknown_person_images')
        self.identified_peoples_dir_path = 'identified_peoples'

        self.streaming = False


        # #----------------- Actions -------------------------
        self.btn_add_faces_window.clicked.connect(self.add_faces_window)
        self.btn_global_settings.clicked.connect(self.to_global_settings_window)
        self.btn_view_db.clicked.connect(self.to_view_db_window)
        self.btn_view_result.clicked.connect(self.to_reports_window)
       
        self.btn_start_stop.clicked.connect(self.start_camera_and_processing)

        app.aboutToQuit.connect(self.stop)

        self.get_global_settings()
        self.initialize_camera_object()
        self.initialize_face_reco_object()

        # self.titles = ['title1','title2']
        ## ---- List widget
        self.img_list = os.listdir(self.identified_peoples_dir_path)     
        self.img_path_list = [os.path.join(self.identified_peoples_dir_path, filename) for filename in self.img_list]
        self.update_list_widget()


    def get_global_settings(self):
        if os.path.exists(self.settings_file_path):
            with open(self.settings_file_path, 'r') as f:               
                lines = f.readlines()
                for line in lines[1:]:
                    line = line.replace('\n','')
                    key, value = line.split(',')
                    if key == 'RTSP_Link':
                        self.rtsp_link = value.strip()
                    if key =='Num_jitters':
                        self.n_jitters = int(value)
                    if key =='Detection_threshold':
                        self.detection_threshold = float(value)



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


    @pyqtSlot(QImage)
    def setImage(self, image):
        self.label_stream_live.setPixmap(QPixmap.fromImage(image))
    

    def initialize_camera_object(self):
        if os.path.exists(self.settings_file_path):
            with open(self.settings_file_path, 'r') as f:               
                lines = f.readlines()
                for line in lines[1:]:
                    line = line.replace('\n','')
                    key, value = line.split(',')
                    if key == 'RTSP_Link':
                        self.rtsp_link = value.strip()
                        
                        ## -----------Start Camera object---------
                        self.camObject = Camera(self.rtsp_link, self.n_jitters ,uiObject = self)
                        
        
        else:
            showdialog("No camera added ! Please add camera in settings!")
            self.to_global_settings_window()

                  
    def initialize_face_reco_object(self):
        
        create_directory(self.main_dir)
        create_directory(self.recording_dir_path)
        create_directory('identified_peoples')

        self.faceDetectionObject = FaceEncodeDecoder(self.trained_enc_directory_path, 
                    self.known_persons_directory_path, 
                    self.Unknown_persons_directory_path)
        print('self.detection_threshold',self.detection_threshold)
        self.faceDetectionObject.n_jitters = self.n_jitters
        self.faceDetectionObject.matching_threshold = self.detection_threshold



    def add_faces_window(self):
        self.initialize_face_reco_object()

        if self.faceDetectionObject is not None:

            self.window = Add_Faces(self.faceDetectionObject, mainUIObject = self)
            self.window.show()
            self.btn_add_faces_window.setStyleSheet('background-color:rgba(216, 229, 253,255); \
                        font: 63 10pt "Segoe UI Semibold"; \
                        color: rgb(64, 109, 255); \
                        border-radius:10; \
                        border:2px solid blue;')
            
    def to_global_settings_window(self):
        self.window = GlobalSettings(mainUIObject=self)
        self.window.show()

    def to_reports_window(self):
        self.window = ReportsView()
        self.window.show()

    def to_view_db_window(self):
        self.window = ViewDB(self)
        self.window.show()


    def start_camera_and_processing(self):
        self.btn_start_stop.disabled= True
        if self.streaming ==False:
            ## ----------------- Start camera object ------------------

            # rtsp_link = 0
            # rtsp_link = "rtsp://admin:hik12345@192.168.1.64:554/Streaming/Channels/2"
            rtsp_link = self.rtsp_link
            recording_dir_path = r'recordings'

            # camObject = Camera(rtsp_link, uiObject = self)

            ### ----------------------- Initialize camObject -----------------------
        
            self.initialize_camera_object()
                

            print('self.streaming',self.streaming)
            print('Self.rtsp_link',self.rtsp_link)
            
            
            if self.camObject is not None:
                
                self.camObject.changePixmap.connect(self.setImage)
                self.camObject.start()
                
                
                # camObject.daemon = True
                self.camObject.recording_dir_path = recording_dir_path
                # camObject.record_stream()
                self.streaming = True
                self.camObject.start_streaming(faceRecoObject=self.faceDetectionObject)

        else:
            print("Stopping the cameraa.........")
            self.camObject.terminate()
            self.camObject.stop()
            self.streaming= False


    def stop(self):
        print('stopping the program......')
        self.camObject.stop()



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    mainScreen = MyMainWindow(app)
    
    widget = QStackedWidget()
    widget.addWidget(mainScreen)
    widget.setFixedHeight(900)
    widget.setFixedWidth(1720)
    widget.show()

    
   

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting..")
