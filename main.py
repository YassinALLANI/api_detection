import os
from app import app
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import cv2
import time
import subprocess
import base64
import requests

CONFIDENCE_THRESHOLD = 0.2
NMS_THRESHOLD = 0.4
COLORS = [(0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 0)]

@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/', methods=['POST'])
def upload_video():
    # if 'file' not in request.files:
    #     flash('No file part')
    #     return redirect(request.url)
    # start new part to be able to read url ##############################################
    print("ccccccccccccccccccccccccccccc")
    url = 'https://actimistorage.blob.core.windows.net/teledentamedia/a49977a2-2755-478e-9f6b-a95496beb816-1657108014315'
    url = request.form['url']
    data = base64.b64encode(requests.get(url).content)
    with open("static/uploads/file.txt", "wb") as fh:
        fh.write(base64.decodebytes(data))
    infile = "static/uploads/file.txt"
    outfile = "static/uploads/cleaned_file.txt"

    delete_list = ["data:video/mp4;base64,"]
    with open(infile) as fin, open(outfile, "w+") as fout:
        for line in fin:
            for word in delete_list:
                line = line.replace(word, "")
            fout.write(line)
    with open(outfile, 'r') as input_file:
        coded_string = input_file.read()
    with open("static/uploads/finalvideo.mp4", "wb") as fh:
        fh.write(base64.b64decode(coded_string))
    # file  = cv2.VideoCapture("static/uploads/finalvideo.mp4")

    filename = 'finalvideo.mp4'
    #end of the new part   ##################################################
    # file = request.files['file']
    # filename = secure_filename(file.filename)
    lst = [filename]
    name , extension = os.path.splitext(lst[0])
    p = os.path.join('data/video/afterDetection', filename)
    # print("exteeeeeeeeeeeeeeention",extension)
    # global id , part
    id = request.form['id']
    part = request.form['part']
    # k = list()
    # k.append(id)
    # k.append(part)
    t = os.path.join(app.config['UPLOAD_FOLDER'], 'partid.txt')
    with open(t,'w') as f:
        f.writelines('{}\n{}\n'.format(id,part))

    if  filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    elif extension in ['.png','.jpg','.jpeg']:

          subprocess.run(
              ['python', 'detect.py', '--weights', './checkpoints/yolov4-416', '--size', '416', '--model', 'yolov4',
               '--images', os.path.join(app.config['UPLOAD_FOLDER'], filename), '--output', p, '--crop', '--count'])


    else:
        # filename = secure_filename(filename)
        # nwli l file name nzidha l id wel part w bead ne5ou menha heka lkol
        # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # print('upload_video filename: ' + filename)
        flash('Video successfully uploaded and displayed below')
        print("hneeeeeeeeeeeeee",filename)

        subprocess.run(['python', 'detect_video.py', '--weights', './checkpoints/yolov4-416', '--size', '416', '--model', 'yolov4','--video', os.path.join(app.config['UPLOAD_FOLDER'], filename), '--output', p, '--crop', '--count'])
        # subprocess.run(
        #     ['python', 'detect.py', '--weights', './checkpoints/yolov4-416', '--size', '416', '--model', 'yolov4',
        #      '--images', os.path.join(app.config['UPLOAD_FOLDER'], filename), '--output', p, '--crop', '--count'])
        print("awed affichiih belehi 5ali nraa :",filename)
        return render_template('upload.html', filename=filename)


@app.route('/display/<filename>')
def display_video(filename):
    # print('display_video filename: ' + filename)
    # hnee nml detection : nkolou hez l video men ghadi w hanou andek l path c deja #
    print("choud be heeeeeeeeree",filename)
    return redirect(url_for('data/video/afterDetection/', filename=filename), code=301)

    # return redirect(url_for('./data/video/afterDetection', filename=filename), code=301)


if __name__ == "__main__":
    app.run()