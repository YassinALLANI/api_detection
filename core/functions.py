import os
import cv2
import random
import numpy as np
import tensorflow as tf
import pytesseract
from core.utils import read_class_names
from core.config import cfg
import requests
import base64
# UPLOAD_FOLDER = 'static/uploads/'
# t = os.path.join('UPLOAD_FOLDER', 'partid.txt')
t = 'static/uploads/partid.txt'


# function to count objects, can return total classes or count per class
def count_objects(data, by_class = False, allowed_classes = list(read_class_names(cfg.YOLO.CLASSES).values())):
    boxes, scores, classes, num_objects = data

    #create dictionary to hold count of objects
    counts = dict()

    # if by_class = True then count objects per class
    if by_class:
        class_names = read_class_names(cfg.YOLO.CLASSES)

        # loop through total number of objects found
        for i in range(num_objects):
            # grab class index and convert into corresponding class name
            class_index = int(classes[i])
            class_name = class_names[class_index]
            if class_name in allowed_classes:
                counts[class_name] = counts.get(class_name, 0) + 1
            else:
                continue

    # else count total objects found
    else:
        counts['total object'] = num_objects
    
    return counts
import os
# function for cropping each detection and saving as new image
def crop_objects(img, data, path, allowed_classes):

    boxes, scores, classes, num_objects = data
    class_names = read_class_names(cfg.YOLO.CLASSES)
    #create dictionary to hold count of objects for image name
    counts = dict()
    for i in range(num_objects):
        # get count of class for part of image name
        class_index = int(classes[i])
        class_name = class_names[class_index]
        if class_name in allowed_classes:
            counts[class_name] = counts.get(class_name, 0) + 1

            try:

                list = os.listdir(path)  # dir is your directory path
                number_files = len(list)

            except:

                number_files = counts.get(class_name, 0) + 1
            # get box coords
            xmin, ymin, xmax, ymax = boxes[i]
            # crop detection from image (take an additional 5 pixels around all edges)
            cropped_img = img[int(ymin)-5:int(ymax)+5, int(xmin)-5:int(xmax)+5]
            #cropped_img = img
            # construct image name and join it to path for saving crop properly
            # img_name = class_name + '_' + str(counts[class_name]) + '.png'
            img_name = class_name + '_' + str(number_files) + '.png'
            img_path = os.path.join(path, img_name )
            file_name = class_name + '_' + str(number_files) + '.json'
            file_path = os.path.join(path, file_name)

            # save image
            try :

                cv2.imwrite(img_path, cropped_img)
                # this part is new now
                # try to convert image to base64
                import base64

                with open(img_path, "rb") as img_file:
                    b64_string = base64.b64encode(img_file.read()).decode('utf-8')
                print("image string is = ", b64_string)
                # l = list()
                # l.append(str(b64_string))
                l = [str(b64_string)]
                print("hneeeeeee fama list ",l)
                # open text file
                # import json
                # columns = {
                #     'data_columns': [i for i in l]
                # }
                # with open(file_path, 'w') as jsonfile:
                #     json.dump(columns, jsonfile)
            except :
                continue
            import json

            # t = os.path.join(app.config['UPLOAD_FOLDER'],'partid.txt')
            f = open(t, 'r')
            n = f.readlines()
            oo = []
            for i in n:
                val = i.strip().split(',')
                oo.append(val[0])
            # print("cooooooooooooooooooooooooooool",oo) // 

            columns = {
                'data_columns': [i for i in l],
                'part-id': [j for j in oo]

            }
            try:
                r = requests.post('https://actimi-middleware-staging.herokuapp.com/crop', json={'data':l[0],'id':oo[0],'part':oo[1]},cookies={'access_token':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Im5lY2RldEBhY3RpbWkuY29tIiwic3ViIjoiYzFiNGQ2NmMtN2VhMC00YTBlLTlkMDQtMjBhOTEwMTJmZjcxIiwicm9sZXMiOlsiUGF0aWVudCJdLCJvcmdhbml6YXRpb24iOiIwMmI4ZTk2NS1hMGQzLTQyMDAtYTRiNi01YjYyMTUyNmZhMjIiLCJuYW1lIjoieWlnaXQgZXJvZ2x1IiwicnVsZXMiOltbInJlYWQsdXBkYXRlLGRlbGV0ZSxzZWFyY2giLCJwYXRpZW50Il0sWyJyZWFkLHNlYXJjaCIsInByYWN0aXRpb25lciJdLFsiY3JlYXRlLHJlYWQsc2VhcmNoLGRlbGV0ZSIsIm9ic2VydmF0aW9uIix7InN1YmplY3QiOiJjMWI0ZDY2Yy03ZWEwLTRhMGUtOWQwNC0yMGE5MTAxMmZmNzEifV0sWyJjcmVhdGUscmVhZCx1cGRhdGUsZGVsZXRlLHNlYXJjaCIsInRyYWluaW5nU2NoZWR1bGVzIl0sWyJjcmVhdGUscmVhZCxzZWFyY2gsdXBkYXRlLGRlbGV0ZSIsIm1lZGljYXRpb25SZXF1ZXN0Il0sWyJjcmVhdGUscmVhZCx1cGRhdGUsZGVsZXRlLHNlYXJjaCIsIm1lZGljYXRpb24iXSxbImNyZWF0ZSxyZWFkLHNlYXJjaCIsInF1ZXN0aW9ubmFpcmUiXSxbImNyZWF0ZSxyZWFkLHNlYXJjaCIsInF1ZXN0aW9ubmFpcmVSZXNwb25zZSJdLFsiY3JlYXRlLHJlYWQsc2VhcmNoIiwicmVzZWFyY2hTdHVkeSJdLFsiY3JlYXRlLHJlYWQsdXBkYXRlLHNlYXJjaCIsIm1lc3NhZ2VzIl0sWyJjcmVhdGUscmVhZCxzZWFyY2giLCJsaW1pdFZhbHVlcyJdLFsicmVhZCxzZWFyY2giLCJ0cmFpbmluZ1Rvb2xzIl0sWyJ1cGRhdGUsY3JlYXRlLHJlYWQsc2VhcmNoIiwidHJhaW5pbmdUb29sc093bmVyc2hpcCJdLFsiY3JlYXRlLHJlYWQsdXBkYXRlLGRlbGV0ZSxzZWFyY2giLCJmaWxlU3lzdGVtIl1dLCJpYXQiOjE2NTgxODAyMjYsImV4cCI6MTY4OTczNzgyNiwiaXNzIjoiaHR0cHM6Ly9hY3RpbWktc3RyYXBpLmhlcm9rdWFwcC5jb20ifQ.yaOFa-O3fy3fLfC9GFkxVvF-xg_6Hy78rgGUK5R2rno', 'Expires':'Mon, 25 Jul 2022 21:37:06 GMT'})
            except:
                print("An exception occurred")
                # e.decode("UTF-8")
                
            # hne najoutie l post request to backend
            with open(file_path, 'w') as jsonfile:
                json.dump(columns, jsonfile)
            print('should be here coloumnssssssssssssssssssssssss ',columns)

        else:
            continue
        
# function to run general Tesseract OCR on any detections 
def ocr(img, data):
    boxes, scores, classes, num_objects = data
    class_names = read_class_names(cfg.YOLO.CLASSES)
    for i in range(num_objects):
        # get class name for detection
        class_index = int(classes[i])
        class_name = class_names[class_index]
        # separate coordinates from box
        xmin, ymin, xmax, ymax = boxes[i]
        # get the subimage that makes up the bounded region and take an additional 5 pixels on each side
        box = img[int(ymin)-5:int(ymax)+5, int(xmin)-5:int(xmax)+5]
        # grayscale region within bounding box
        gray = cv2.cvtColor(box, cv2.COLOR_RGB2GRAY)
        # threshold the image using Otsus method to preprocess for tesseract
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        # perform a median blur to smooth image slightly
        blur = cv2.medianBlur(thresh, 3)
        # resize image to double the original size as tesseract does better with certain text size
        blur = cv2.resize(blur, None, fx = 2, fy = 2, interpolation = cv2.INTER_CUBIC)
        # run tesseract and convert image text to string
        try:
            text = pytesseract.image_to_string(blur, config='--psm 11 --oem 3')
            print("Class: {}, Text Extracted: {}".format(class_name, text))
        except: 
            text = None

