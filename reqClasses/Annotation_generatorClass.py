from traceback import print_tb
import xml.etree.ElementTree as eTree
import os
import cv2 ## 


class AnnotationGenerator:
    def __init__(self, imgs_n_annotions_dir_path ) -> None:
        """
        Params : 
        imgs_n_annotions_dir_path : Path of folder where images to be annotated and annotations will be saved 
        
        """
        self.folderPath_to_save = imgs_n_annotions_dir_path
        self.__sub_element_list = ['folder','filename','path','source','size','segmented']


        self.annotation_type = "PascalVOC_XML"
        self.n_images_to_generate = 100
        self.vid_or_cam_path = ""
        self.obj_label_to_annotation =""
        self.isSourceCamera = False
        ### Types of annotations to be saved 
        # 1. "PascalVOC_XML"
        # 2. "YOLO_txt file"
    def generate_annotations_using_tracker(self):
        self.__get_user_inputs_for_annotation_generator()
        self.__generate_annotations_using_tracker(self.vid_or_cam_path)


    def __get_user_inputs_for_annotation_generator(self):

        #####
        # source of video /cam
        # object label or name to create annotation for
        # no of images to create annoations
        # annotation type 

        vid_or_cam_source = input("What you want to annotate a Video file(0) or using Camera stream (1) (0 or1):")
        while vid_or_cam_source not in ["0", "1"]:
            print('Please provide correct input..')
            vid_or_cam_source = input("What you want to annotate a Video file(0) or using Camera stream (1) (0 or1):")

        if int(vid_or_cam_source) == 0:
            vidPath = input("Please input a video path :")
            while not os.path.exists(vidPath):
                print("Input path does not exist..")
                vidPath = input("Please input a video path :")
            self.vid_or_cam_path = vidPath
        elif int(vid_or_cam_source) == 1:
            camSource = input("Please input a camera source (0 or other) :")
            while not camSource.isnumeric():
                print('Please provide correct input..')
                camSource = input("Please input a camera source (0 or other) :")
            
            self.vid_or_cam_path = int(camSource)
            self.isSourceCamera = True



        # self.vid_or_cam_path = vid_or_cam_source

        obj_label = input("Please input object label to annotate :")
        while len(obj_label)==0:
            obj_label = input("Please input object label to annotate :")

        self.obj_label_to_annotation = obj_label
        
        n_images_to_annotate =  input("How many image annotations do you want to generate? :")
        while not n_images_to_annotate.isnumeric():
            n_images_to_annotate =  input("How many image annotations do you want to generate? :")

        self.n_images_to_generate = n_images_to_annotate

        print("Select annotation file type that you want to generate :")
        print("1. xml File Pascal VOC : ")
        print("2. txt File YOLO V4 : ")
        
        annotation_type = input("Please enter option (1 or 2): ")
        while annotation_type not in ["1", "2"]:
            annotation_type = input("Please enter option (1 or 2): ")

        if int(annotation_type)==1:
            self.annotation_type ="PascalVOC_XML"
        elif int(annotation_type)==2:
            self.annotation_type ="YOLO_txt"

        print('Done !! ready to go...')


        
    def __generate_annotations_using_tracker(self, vid_or_cam_path):
        """Generate annotation using camera of video and Using Opencv Tracker algorithm
        Param : camPath : video or camera source path for capture device, put  0 for webcam

        Return : Generate images, save, generate csv file with annotations, also generate xml or txt annotation
        and save them 
        """
        print("self.vid_or_cam_path", self.vid_or_cam_path)
        print(type(self.vid_or_cam_path))
        cap = cv2.VideoCapture(self.vid_or_cam_path)
        tracker = cv2.legacy.TrackerCSRT_create()

        if self.isSourceCamera:
            imgName_to_save = "cam"
        else:
            vidName = os.path.basename(vid_or_cam_path)
            vidName_wo_ext = vidName.split(".")[0]
            imgName_to_save = vidName_wo_ext


        ret, firstFrame = cap.read()
        if ret:
            bbox = cv2.selectROI('Select ROI', firstFrame)
            tracker.init(firstFrame, bbox)
        else:
            print('No stream found for path', self.vid_or_cam_path)

        frameNo = 0
        cnt_frame_saved = 1
        w_img = cap.get(cv2.CAP_PROP_FRAME_WIDTH) 
        h_img=  cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        ch_img = 3
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break

            frameToSave = frame.copy()
            gotBox, bbox = tracker.update(frame)
            if gotBox:
                (x,y,w,h) = [int(v) for v in bbox]
                frame = cv2.rectangle(frame, (x,y),(x+w,y+h), (0,255,0),2)
                if frameNo%5==0:
                    imgName = f"{imgName_to_save}_{str(cnt_frame_saved)}.png"
                    imgPath = os.path.join(self.folderPath_to_save, imgName)
                    cv2.imwrite(imgPath, frameToSave)
                    cnt_frame_saved+=1
                    frame = cv2.putText(frame, f"Annotations saved count : {cnt_frame_saved}",
                    (10,20),cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2)
                    obj_annotation_list = [self.obj_label_to_annotation, x,y,x+w,y+h]

                    if self.annotation_type=="PascalVOC_XML":
                        self.create_xml_annotation_obj_detection_PascalVOC(imgName, imgPath,obj_annotation_list, w_img, h_img, ch_img)
                    elif self.annotation_type=="YOLO_txt":
                        ### write logic here
                        pass
                    
                  
            cv2.imshow('Annotate Frames Using Tracker algorithm',frame)
            frameNo+=1
            key = cv2.waitKey(1)
            if key == "q":
                break


    def create_xml_annotation_obj_detection_PascalVOC(self, imgName, imgPath, obj_annotation_list, w_img, h_img, ch_img):
        """ Create XML annotation format PascalVOC 
        Param : 

        """
        
        
        root = eTree.Element('annotation')
        for subElement in self.__sub_element_list:
            s1 = eTree.Element(subElement)
            root.append(s1)
            if subElement=='folder':
                s1.text = self.folderPath_to_save
            elif subElement=='filename':
                s1.text = imgName
            elif subElement=='path':
                s1.text = imgPath

            elif subElement=='size':
                w1 = eTree.SubElement(s1,'width')
                w1.text = str(w_img)
                h2 = eTree.SubElement(s1,'height')
                h2.text = str(h_img)
                d1 = eTree.SubElement(s1,'depth')
                d1.text = str(ch_img)
            if subElement=='source':
                db_el = eTree.SubElement(s1,'database')
                db_el.text ='Unknown'
            if subElement=='segmented':
                s1.text=str(0)


        for eachObjAnnotation in obj_annotation_list:

            objLabel, xmin, ymin, xmax, ymax = eachObjAnnotation
            s1 = eTree.Element('object')        
            
            nameEle = eTree.SubElement(s1,'name')
            nameEle.text = objLabel
            poseEle = eTree.SubElement(s1,'pose')
            poseEle.text = "Unspecified"
            truEle = eTree.SubElement(s1, 'truncated')
            truEle.text = str(1)
            diffEle = eTree.SubElement(s1, 'difficult')
            diffEle.text = str(0)
            bndBoxEle = eTree.SubElement(s1,'bndbox')
            xminEle = eTree.SubElement(bndBoxEle, 'xmin')
            xminEle.text = str(xmin)
            yminEle = eTree.SubElement(bndBoxEle, 'ymin')
            yminEle.text = str(ymin)
            xmaxEle = eTree.SubElement(bndBoxEle, 'xmax')
            xmaxEle.text = str(xmax)
            ymaxEle = eTree.SubElement(bndBoxEle, 'ymax')
            ymaxEle.text = str(ymax)
            root.append(s1)

            
        fileNameWo_ext = imgName.split(".")[0]
        xmlFileName = fileNameWo_ext + ".xml"

        xmlFilePath = os.path.join(self.folderPath_to_save, xmlFileName)
        tree = eTree.ElementTree(root)
        eTree.indent(tree)
        # eTree.indent(tree, level=1)
        # eTree.indent(tree, level=2)

        with open(xmlFilePath,'wb') as f:
            tree.write(f, short_empty_elements=False)

