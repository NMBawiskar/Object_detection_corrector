import os
import cv2
from objDetection.yoloV5Inference_class import YoloV5ObjDetector
from reqClasses.Annotation_generatorClass import AnnotationGenerator


model_weights_file_path = r'projects\aadhar_masking\model_weights\aadhar_masking_best.pt'
yaml_file_path = r'projects\aadhar_masking\dataset.yaml'
imagesDIR = r'projects\aadhar_masking\images_to_check_inference_on'



annotations_generator =  AnnotationGenerator(imagesDIR)

yoloV5ObjDetector = YoloV5ObjDetector(model_weights_file_path)
yoloV5ObjDetector.load_labels(yaml_file_path=yaml_file_path)

imageExtenstions = ['jpg','jpeg','bmp','png','tiff']

images = os.listdir(imagesDIR)
images = [file for file in images if file.split(".")[-1] in imageExtenstions]
for imgFile in images:
    pathImg = os.path.join(imagesDIR, imgFile)
    resultCombinedDict = yoloV5ObjDetector.get_predictions(pathImg)
    
    data_annotations = [] ##  objLabel, xmin, ymin, xmax, ymax,
    imgCv2 = cv2.imread(pathImg)
    hImg, wImg, chImg = imgCv2.shape

    for label, annotationsList in resultCombinedDict.items():
        for annotationDict in annotationsList:
            xmin, ymin, xmax, ymax = annotationDict['xmin'], annotationDict['ymin'], annotationDict['xmax'], annotationDict['ymax']
            list_each_annotation = [label, xmin, ymin, xmax, ymax]
            data_annotations.append(list_each_annotation)

    ### Create pascalVOC xml fille
    print("====")
    print("data_annotations",data_annotations)
    annotations_generator.create_xml_annotation_obj_detection_PascalVOC(imgName=imgFile, imgPath=pathImg, obj_annotation_list=data_annotations,
        w_img=wImg, h_img=hImg, ch_img=chImg)

    print("result")
