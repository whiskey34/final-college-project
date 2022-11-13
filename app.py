import sqlite3
from flask import Flask, redirect, url_for, render_template, jsonify, flash, Response, request, session
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Boolean
from sqlalchemy.orm import sessionmaker, relationship, backref


import os
import cv2
import json
import pandas as pd
import csv

from core_service.dl_core_main import TransferLearning
from core_service.facerecognition import Recognizer
from models import Record_absen
from __init__ import app, db

socketio = SocketIO(app)


PATH = '\\'.join(os.path.abspath(__file__).split('\\')[0:-1])


recognizer = Recognizer(
    socketio=socketio,
    facerecognition_model=os.path.join(
        PATH, "core_service\\bin\\simple_frozen_graph.pb"),
    labels_filename=os.path.join(PATH, "core_service\\labels.csv"),
    facedetection_model=os.path.join(
        PATH, "core_service\\bin\\haarcascade_frontalface_default.xml"),
    use_mtcnn=False,
    camera_src=0
)


@app.route("/", methods=['POST', 'GET'])
def index():
    camera = request.args.get("camera")

    if camera is not None and camera == 'off':
        recognizer.close()
        flash("Camera turn off!", "info")
    elif camera is not None and camera == 'on':
        recognizer.open()
        flash("Camera turn on!", "success")
    print("camera status", recognizer.status())
    return render_template("index.html", is_camera=recognizer.status())


@app.route("/history", methods=['POST', 'GET'])
def history():

    return render_template('history.html')


@app.route("/face_registration")
def face_registration():
    return render_template('face_registration.html')


@app.route("/record_data", methods=['GET', 'POST'])
def record_data():
    if request.method == 'POST':
        engine = create_engine(
            'sqlite:///recogweb.db', echo=True, connect_args={"check_same_thread": False})
        Session = sessionmaker(bind=engine)
        session = Session()

        send_back = {"status": "failed"}

        try:
            # data = request.get_json()
            data = request.json
            # return jsonify(data)
            print('data :', data)

            # data = Record_absen(1, "abang", "masuk", "gambar.jpg")
            rec = Record_absen(data['label'], data['status'], data['img'])
            session.add(rec)
            session.commit()
            send_back["status"] = "success"
        except:
            send_back["status"] = "Error"
        return jsonify(send_back)

    return redirect(url_for('index'))


@app.route("/video_feed")
def video_feed():
    return Response(recognizer.gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/print_csv", methods=['GET'])
def print_csv():
    conn = sqlite3.connect('recogweb.db')
    cursor = conn.cursor()
    cursor.execute("select * from record_absen;")
    with open("data_absensi.csv", 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([i[0] for i in cursor.description])
        csv_writer.writerows(cursor)
    conn.close()
    return (url_for('history'))


@app.route("/upload_photo", methods=['POST'])
def upload_photo():
    class_name = request.args.get('class_name')
    path_new_class = os.path.join(os.path.join(PATH, "..\dataset"), class_name)

    # create directory label if not exist
    if not os.path.exists(path_new_class):
        os.mkdir(path_new_class)

    # save uploaded image
    filename = class_name + '%04d.jpg' % (len(os.listdir(path_new_class)) + 1)
    file = request.files['webcam']
    file.save(os.path.join(path_new_class, filename))

    # resize
    img = cv2.imread(os.path.join(path_new_class, filename))
    img = cv2.resize(img, (250, 250))
    cv2.imwrite(os.path.join(path_new_class, filename), img)

    tl.dim = len(os.listdir(os.path.join(PATH, "..\dataset")))

    return '', 200


@app.route("/transfer_learning")
def transfer_learning():
    return render_template("transfer_learning.html")
# ------------------ Khusus SocketIO ----------------------


@ socketio.on('run')
def handle_message(message):
    if not tl.is_running:
        socketio.start_background_task(target=tl.run)
    else:
        socketio.emit("feedback", "Transfer Learning already running.")


@ socketio.on('check')
def handle_message(message):
    print("status", tl.is_running)
    socketio.emit("status", tl.is_running)


if __name__ == '__main__':
    global tl
    tl = TransferLearning(socketio,
                          event="feedback",
                          model_name=os.path.join(
                              PATH, "core_Service\\bin\\My_model.h5"),
                          dim=len(os.listdir(os.path.join(PATH, "..\dataset"))),
                          dataset=os.path.join(PATH, "..\dataset"),
                          use_augmentation=False,
                          epoch=10)

    tl.init_model()

    socketio.run(app)
