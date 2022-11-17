import torch
import cv2
import os
import yaml

class YoloV5ObjDetector:
    def __init__(self, model_weights_path):
        
        """"""

        self.model_weights_path = model_weights_path  ## Path to best.pt trained model weights
        self.model = None        
        self.data_labels = {}  ### ex 1:'aadhar_photo', 2:"qr_code"

        self.color_list = [(255,0,0), (0,255,0),(0,0,255),(255,255,0), (0,255,255),(255,0,255), 
             (127,127,0), (0,127,127),(127,0,127) ]
        self.load_model()

    def load_model(self):
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', self.model_weights_path)


    def load_labels(self, yaml_file_path='', list_labels = []):
        """Loads labels from dataset.yaml file while training yolov5 or from list_labels 
        param : provide any one of list_labels or yaml_file_path
        
        
         """

        if len(list_labels)==0 and len(yaml_file_path)== 0:
            print('Please provide any one of the lables list or yaml file path....')
            return False
        else:
            
            if len(yaml_file_path)!= 0:
                if os.path.exists(yaml_file_path):
                    with open(yaml_file_path, "r") as stream:
                        try:
                            data_training = (yaml.safe_load(stream))
                            self.data_labels = data_training['names']
                        except yaml.YAMLError as exc:
                            print(exc)

                else:
                    print('Please provide correct yaml file path....')
        
            if len(list_labels)>0:

                for i, label in enumerate(list_labels):
                    self.data_labels[i] = label


        print("Loaded lables dictionary == ",self.data_labels)


    def get_predictions(self, imgPath):
        # Inference
        results = self.model(imgPath)

        dict_combined = {}

        # print(results.xyxy[0])  # im predictions (tensor)
        df = results.pandas().xyxy[0]
        print(results.pandas().xyxy[0])  #im predictions (pandas)
        print(type(df))
        dict_result = df.to_dict('records')
        # print("dict_result",dict_result)
        for dict_values in dict_result:
            if dict_values['name'] not in dict_combined:
                dict_combined[dict_values['name']] = []
            


            dict_combined[dict_values['name']].append(dict_values)
        
        print("dict_combined",dict_combined)
        return dict_combined

    def mask_results(self, dict_result, imgPath):
        img = cv2.imread(imgPath)
        for obj, list_detections in dict_result.items():

            color_border = self.color_list[obj]
            for eachDet in list_detections:
                xmin = int(eachDet['xmin'])
                ymin = int(eachDet['ymin'])
                xmax = int(eachDet['xmax'])
                ymax = int(eachDet['ymax'])
                conf = eachDet['confidence']
                cv2.rectangle(img, (xmin,ymin),(xmax,ymax),color_border, 2)
                if obj == "aadharNo":
                    w_obj= xmax - xmin
                    h_obj= ymax-ymin
                    if w_obj <h_obj:
                        ## Text is vertical
                        cv2.rectangle(img, (xmin,ymin), (xmax, int(ymin+0.66*h_obj)), (127,127,127),-1)

                    else:
                        ## Text is horizontal
                        cv2.rectangle(img, (xmin,ymin), (int(xmin+0.66*w_obj), ymax), (127,127,127),-1)
                        
        
        cv2.imshow('Result',img)
        