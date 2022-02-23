#!/usr/bin/env python3
# license removed for brevity
import rospy
from std_msgs.msg import String
from sensor_msgs.msg import NavSatStatus, NavSatFix
import numpy as np
import tkinter
import PIL.Image, PIL.ImageTk
import time
import signal
from PIL.ExifTags import GPSTAGS
from PIL.ExifTags import TAGS
from math import floor
import piexif
import datetime
import os


class Geotagger:
    def __init__(self):

        # Set signal handler
        signal.signal(signal.SIGINT, self.sigint_handler)

        # Ros setup
        rospy.init_node('ExpoGeotagger', anonymous=True)
        self.gps_sub = rospy.Subscriber('dgps_ublox/dgps_base/fix', NavSatFix, self.gps_callback)
        self.last_gps_msg = NavSatFix()
        self.rate = rospy.Rate(10) # 10hz

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update()

    def geotag(self, file_s):
            exif_dict = piexif.load(file_s)
            if exif_dict['GPS'] is None:
                exif_dict['GPS'] = []
            timestamp = datetime.datetime.utcfromtimestamp(float(self.last_gps_msg.header.stamp.secs + (self.last_gps_msg.header.stamp.nsecs * 1e-9)))
            latitude = longitude = (0,0,0)
            altitude = 0
            if np.isnan(self.last_gps_msg.latitude) == False:
                latitude = self.get_dms_from_decimal(float(self.last_gps_msg.latitude))
                longitude = self.get_dms_from_decimal(float(self.last_gps_msg.longitude))
                altitude = self.last_gps_msg.altitude
            gps_ifd = {
                    piexif.GPSIFD.GPSDateStamp: (timestamp.strftime("%d:%m:%Y")),
                    piexif.GPSIFD.GPSTimeStamp: ((timestamp.hour,1), (timestamp.minute,1), (timestamp.second,1)),
                    piexif.GPSIFD.GPSVersionID: (2,3,0,0),
                    piexif.GPSIFD.GPSLatitude: ((int(latitude[0]),1),(int(float(latitude[1])*100),100),(int(float(latitude[2])*1000000),1000000)),
                    piexif.GPSIFD.GPSLatitudeRef: 'N' if latitude[0] >= 0 else 'S',
                    piexif.GPSIFD.GPSLongitude: ((int(longitude[0]),1),(int(float(longitude[1])*100),100),(int(float(longitude[2])*1000000),1000000)),
                    piexif.GPSIFD.GPSLongitudeRef: 'E' if longitude[0] >= 0 else 'W',
                    piexif.GPSIFD.GPSAltitude: (int(altitude*100),100),
                    piexif.GPSIFD.GPSAltitudeRef: (int(0))
            }
            exif_dict['GPS'] = gps_ifd
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, file_s)


    def update(self):
        pass
    
    def gps_callback(self,msg):
        self.last_gps_msg = msg

    def sigint_handler(self, sig, frame):
        self.update()
        exit()

    def get_dms_from_decimal(self, decimal):
        degrees = floor(decimal)
        minutes = floor((decimal - degrees) * 60.0)
        seconds = round((decimal - degrees  - minutes / 60.0 ) * 3600.0, 12)
        return (degrees, minutes, seconds)






