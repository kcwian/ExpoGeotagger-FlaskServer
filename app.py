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

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = "./images"
global i

def geotag(file_s):
            exif_dict = piexif.load(file_s)
            if exif_dict['GPS'] is None:
                exif_dict['GPS'] = []
            timestamp = 13.0 #datetime.datetime.utcfromtimestamp(float(self.last_gps_msg.header.stamp.secs + (self.last_gps_msg.header.stamp.nsecs * 1e-9)))
            latitude = (52, 24, 34.3)#self.get_dms_from_decimal(float(self.last_gps_msg.latitude))
            geotag.counter += 1
            longitude = (16, 56, geotag.counter/5.0) #self.get_dms_from_decimal(float(self.last_gps_msg.longitude))
            altitude = 16#self.last_gps_msg.altitude
            # timestamp.time()
            gps_ifd = {
                  #  piexif.GPSIFD.GPSDateStamp: (timestamp.strftime("%d:%m:%Y")),
                  #  piexif.GPSIFD.GPSTimeStamp: ((timestamp.hour,1), (timestamp.minute,1), (timestamp.second,1)),
                    piexif.GPSIFD.GPSVersionID: (2,3,0,0),
                    piexif.GPSIFD.GPSLatitude: ((int(latitude[0]),1),(int(float(latitude[1])*100),100),(int(float(latitude[2])*1000000),1000000)),
                    piexif.GPSIFD.GPSLatitudeRef: 'N' if latitude[0] >= 0 else 'S',
                    piexif.GPSIFD.GPSLongitude: ((int(longitude[0]),1),(int(float(longitude[1])*100),100),(int(float(longitude[2])*1000000),1000000)),
                    piexif.GPSIFD.GPSLongitudeRef: 'E' if longitude[0] >= 0 else 'W',
                    piexif.GPSIFD.GPSAltitude: (int(altitude*100),100),
                    piexif.GPSIFD.GPSAltitudeRef: (int(0))
            }
            exif_dict['GPS'] = gps_ifd
            # exif_dict['latitude'] = 13.331
            # exif_dict['longitude'] = 11.1231
            # exif_dict['location'] = []
            # gps_location = {
            #   "latitude" : 1.23,
            #   "longitude" : 2.31
            # }
            # exif_dict["location"] = gps_location
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, file_s)
geotag.counter = 0

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
            geotag(file_path)
            #img_base64 = base64.b64encode(open(filename, "rb").read()).decode("ascii")
            img_base64 = base64.b64encode(open(file_path, "rb").read()).decode("ascii")
            return jsonify({"base64" : img_base64, "name" : file_name})

  return jsonify(["Error"])

if __name__ == '__main__':
  app.run(host='0.0.0.0')
