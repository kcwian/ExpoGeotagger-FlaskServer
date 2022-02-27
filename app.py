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

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = "./images"

@app.route('/')
def hello_name():
  return 'Hello!'

@app.route('/image', methods=["POST", "GET"])
def image():
  if request.method == "POST":
        if request.files:
            image = request.files["image"]
            file_name = "IMG-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg"
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file_name)
            image.save(file_path)
            print("Image saved to ", file_path)
            geotagger.geotag(file_path)
            img_base64 = base64.b64encode(open(file_path, "rb").read()).decode("ascii")
            return jsonify({"base64" : img_base64, "name" : file_name})
  return jsonify(["Error"])

@app.route('/dgps', methods=["GET"])
def dgps():
  if request.method == "GET":
        status = geotagger.get_status()
        dgps.counter += 1
        return jsonify({"status" : dgps.counter})
dgps.counter = 0

if __name__ == '__main__':
  geotagger = Geotagger()
  app.run(host='0.0.0.0', threaded=True)