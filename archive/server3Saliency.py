# -*- coding: utf-8 -*-

import os
from flask import Flask, jsonify, request
import json
import jsonschema

from iai_toolbox import AnalyticsRequest, AnalyticsAgent, get_analytics_pool
import time

import face_recognition
from PIL import Image

from scipy.spatial import distance as dist
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from imutils.video import WebcamVideoStream
from imutils import face_utils
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2

"""
C3ISP export utility.
"""

__author__ = "Vincenzo Farruggia"
__license__ = "GPL"
__version_info__ = ('2021','10','28')
__version__ = ''.join(__version_info__)

app = Flask(__name__)
DEBUG=('DEBUG' in os.environ and os.environ['DEBUG'] in ['1', 'true'])


"""
Sample definition of Analytics for IAI integration.
The class have to subclass AnalyticsAgent ones.
The latter will handle all the interaction with C3ISP IAI framework.

User needs to implements both methods run(), end() in order to handle the start and the correct termination of analytics.

Also, user needs to call the on_finish() function when analytics ends in order to signal termination to IAI.
"""
class SampleAnalytics(AnalyticsAgent):    
    def run(self):
        app.logger.info("--- run() started!")

        # Hints:
        # - self.params.iai_files will contains input files to process
        # - self.read_input('dopid') will read input file from datalake
        # - self.write_output('filename', 'content') will write content to datalake

        # do real analytics here
        for infile in self.params.iai_files:
            app.logger.info("- Processing {}".format(infile))
            content = self.read_input(infile)
            app.logger.info('[dump input:{}]: {}'.format(infile, content))
            time.sleep(1)
        
            #------------------------------
            #------------------------------
            #------------------------------
            
            frame = cv2.imread("./tmp/testiai/frameServer2RF.jpg")
            height, width, channels = frame.shape
            print (height, width, channels)
            print ("Dimensions:", frame.shape, "Total pixels:", width * height)

            y = 150
            x = 120

            y = 150
            x = 220

            top1 = int((height/2) - y)
            left1 = int((width/2) - x)
            bottom1 = int((height/2) + y)
            right1 = int((width/2) + x)

            print(top1, left1, bottom1, right1)

            im1 = frame[top1:bottom1, left1:right1]
            face_locations = face_recognition.face_locations(frame)#im1

            print("Found {} faces in the frame.".format(len(face_locations)))

            for face_location in face_locations:
                top, right, bottom, left = face_location
                # print("Face is located at location top: {}, left: {}, bottom: {}, right: {}".format(top, left, bottom, right))
                
                face_image = frame[top:bottom, left:right]
                pil_image = Image.fromarray(face_image)
                pil_image.save('./tmp/testiai/faceServer3S.jpg')
                
                #---------------------------------
                #---------------------------------
                #---------------------------------

            plaintext_output = "Succesfully extracted face - Server3Salinecy"

        # Because write_output will manage byte streams we need to convert string to
        # bytes content
        plaintext_output = str(plaintext_output).encode('utf-8','ignore')
        self.write_output('outfileServer3Salinecy', plaintext_output)

        app.logger.info('--- run() ended!')

        # when analytics finished do callback to server
        success = True
        value = "Face recognition analytic finished with success!!!"
        results = []
        self.on_finish(success, value, results)

    def end(self):
        app.logger.info('--- Termination request for analytics')
        # insert code here for graceful terminate analytics
        # and after signal IAI for termination

        success = False
        value = "Face recognition analytic interrupted!!!"
        results = []
        self.on_finish(success, value, results)

@app.route("/startAnalytics", methods = ['POST'])
def do_start_analytics():
  payload = request.json
  
  jsonschema.validate(payload, AnalyticsRequest.SCHEMA)

  app.logger.debug('New request: {}'.format(payload))


  try:
    iai_req = AnalyticsRequest.from_params(payload)
    # Create analytics process object
    process = SampleAnalytics(iai_req)

    analytics_pool = get_analytics_pool()
    # Add analytics process to the pool of running analytics
    analytics_pool.add(process)

    # Start analytics
    process.start()

    #
    # Return 204 (empty response) when the processing doesn't produce output files
    # to be stored into ISI
    # Otherwise return HTTP 200 status with json array containing paths of the
    # files which will be stored into ISI.
    #
    # IMPORTANT: All the files have to be placed inside the datalake provided
    # 
    return ('', 204)

    # return (jsonify(['file1.ext', 'file2.ext']), 200)
  except Exception as e:
    app.logger.exception(e)
    return (jsonify({'error': 'Error occured'}), 500)


@app.route('/stopAnalytics', methods = ['PUT'])
def do_stop_analytics():
  session_id = request.args.get('session_id')

  try:
    # Retrieve running analytics from pool
    analytics_pool = get_analytics_pool()
    process = analytics_pool.get(session_id)

    # Signal analytics to terminate
    process.terminate()

    analytics_pool.remove(session_id)

    return ('', 204)
  except KeyError:
    return (jsonify({'error': 'Analytics {} not running'.format(session_id)}), 500)
  except Exception as e:
    app.logger.exception(e)
    return (jsonify({'error': 'Error occured'}), 500)



if __name__ == '__main__':
  app.run(host = '0.0.0.0', port = 5001, debug = DEBUG)