from flask import Flask
from flask import Flask, flash, request, redirect, url_for
import os
from flask import jsonify
import numpy as np 
import cv2
import base64
import time
import piexif
import datetime
from geotagger import Geotagger
import json

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = "./images"

@app.route('/')
def hello_name():
  return 'Hello!'

@app.route('/image', methods=["POST", "GET"])
def image():
  if request.method == "POST":
        if request.files:
            platform = request.form["platform"]
            image = request.files["image"]
            GPS_data = json.loads(request.form["GPS"])
            file_name = "IMG-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg"
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file_name)
            image.save(file_path)
            print("Image saved to ", file_path)
            try:
              geotagger.geotag(file_path, platform, GPS_data)
            except Exception as e:
              print("Error: ", e)
            print("Image Geotagged")
            img_base64 = base64.b64encode(open(file_path, "rb").read()).decode("ascii")
            os.remove(file_path)
            print("Image deleted")
            return jsonify({"base64" : img_base64, "name" : file_name})
  return "erro", 400

@app.route('/dgps', methods=["GET"])
def dgps():
  if request.method == "GET":
        status = geotagger.get_status()
        return jsonify({"status" : status})
dgps.counter = 0
dgps.status = 0

@app.route('/lastMessage', methods=["GET"])
def lastMessage():
  if request.method == "GET":
        lastMsg = geotagger.get_last_msg()
        try:
          jsonData = jsonify({"seq" : lastMsg.header.seq, "status" : lastMsg.status.status, "latitude": lastMsg.latitude, 
                          "longitude" : lastMsg.longitude, "altitude" : lastMsg.altitude, "timestamp" : lastMsg.header.stamp.secs + lastMsg.header.stamp.nsecs/1e9 })
        except Exception as e:
          print(e)
        return jsonData

if __name__ == '__main__':
  geotagger = Geotagger()
  # geotagger.geotag("./images/test.jpg", "android")
  # exit(0)
  app.run(host='0.0.0.0', threaded=False)
