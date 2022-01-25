# -*- coding: utf-8 -*-

import os
from flask import Flask, jsonify, request
import json
import jsonschema

from iai_toolbox import AnalyticsRequest, AnalyticsAgent, get_analytics_pool
import time

#-----------------------------------------------------------------
#-----------------------------------------------------------------
#-----------------------------------------------------------------
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
from tqdm import tqdm
#-----------------------------------------------------------------
#-----------------------------------------------------------------
#-----------------------------------------------------------------

"""
C3ISP export utility.
"""

__author__ = "Vincenzo Farruggia"
__license__ = "GPL"
__version_info__ = ('2021','11','30')
__version__ = ''.join(__version_info__)

app = Flask(__name__)
DEBUG=('DEBUG' in os.environ and os.environ['DEBUG'] in ['1', 'true'])

#-----------------------------------------------------------------
#-----------------------------------------------------------------
#-----------------------------------------------------------------
def eye_aspect_ratio(eye):
    # compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    # compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = dist.euclidean(eye[0], eye[3])
    # compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)
    # return the eye aspect ratio
    return ear
#-----------------------------------------------------------------
#-----------------------------------------------------------------
#-----------------------------------------------------------------

"""
Sample definition of Analytics for IAI integration.
The class have to subclass AnalyticsAgent ones.
The latter will handle all the interaction with C3ISP IAI framework.

User needs to implements both methods run(), end() in order to 
handle the start and the correct termination of analytics.

Also, user needs to call the on_finish() function when analytics ends in order
to signal termination to IAI.
"""
class SampleAnalytics(AnalyticsAgent):
  def run(self):
    app.logger.info("--- run() started!")

    # Hints:
    # - self.params.iai_files will contains input files to process
    # - self.read_input('dopid') will read input file from datalake
    # - self.write_output('filename', 'content') will write content to datalake

    # do real analytics here
    
    #-----------------------------------------------------------------
    #-----------------------------------------------------------------
    #-----------------------------------------------------------------
    EYE_AR_THRESH = 0.20
    EYE_AR_CONSEC_FRAMES = 1
    COUNTER = 0
    TOTAL = 0
    
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('./face_recognition_models/models/spfl.dat')
    
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
    
    vs = cv2.VideoCapture("./tmp/testiai/k.mp4")
    length = int(vs.get(cv2.CAP_PROP_FRAME_COUNT))
    
    time.sleep(1.0)
    #-----------------------------------------------------------------
    #-----------------------------------------------------------------
    #-----------------------------------------------------------------
    for infile in self.params.iai_files:
        app.logger.info("- Processing {}".format(infile))
        content = self.read_input(infile)
        app.logger.info('[dump input:{}]: {}'.format(infile, content))
        time.sleep(2)
            
        for x in range(length):
            ret, frame = vs.read()
            frame = imutils.resize(frame, width=450)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rects = detector(gray, 0)

            for rect in rects:
                shape = predictor(gray, rect)
                shape = face_utils.shape_to_np(shape)
                leftEye = shape[lStart:lEnd]
                rightEye = shape[rStart:rEnd]
                leftEAR = eye_aspect_ratio(leftEye)
                rightEAR = eye_aspect_ratio(rightEye)
                ear = (leftEAR + rightEAR) / 2.0
                leftEyeHull = cv2.convexHull(leftEye)
                rightEyeHull = cv2.convexHull(rightEye)
                if ear < EYE_AR_THRESH:
                    COUNTER += 1
                    cv2.imwrite('./tmp/testiai/frameServer2RF.jpg', frame)
                    realFrame = frame
                    break
                else:
                    if COUNTER >= EYE_AR_CONSEC_FRAMES:
                        TOTAL += 1
                    COUNTER = 0
                    
                #------------------------------
                #------------------------------
                #------------------------------
                
        # frame = cv2.imread("./tmp/testiai/frameServer2RF.jpg")
        height, width, channels = realFrame.shape
        print (height, width, channels)
        # print ("Dimensions:", frame.shape, "Total pixels:", width * height)

        y = 150
        x = 120

        y = 150
        x = 220

        top1 = int((height/2) - y)
        left1 = int((width/2) - x)
        bottom1 = int((height/2) + y)
        right1 = int((width/2) + x)

        # print(top1, left1, bottom1, right1)

        im1 = realFrame[top1:bottom1, left1:right1]
        face_locations = face_recognition.face_locations(realFrame)#im1

        # print("Found {} faces in the frame.".format(len(face_locations)))

        for face_location in face_locations:
            top, right, bottom, left = face_location
            # print("Face is located at location top: {}, left: {}, bottom: {}, right: {}".format(top, left, bottom, right))
            
            face_image = realFrame[top:bottom, left:right]
            pil_image = Image.fromarray(face_image)
            # pil_image.save('./tmp/testiai/faceServer3S.jpg')
            
            #-------------------------------------
            #-------------------------------------
            #-------------------------------------
            kous_image = face_recognition.load_image_file("./tmp/testiai/7.png")
            kous_face_encoding = face_recognition.face_encodings(kous_image)[0]

            #test_image = face_recognition.load_image_file("./tmp/testiai/faceServer3S.jpg")
            test_image = np.array(pil_image)
            test_face_encoding = face_recognition.face_encodings(test_image)[0]
            
            plaintext_output = face_recognition.compare_faces([kous_face_encoding], test_face_encoding)
            break
        #-----------------------------------------------------------------
        #-----------------------------------------------------------------
        #-----------------------------------------------------------------

    # Because write_output will manage byte streams we need to convert string to
    # bytes content
    plaintext_output = str(plaintext_output[0]).encode('utf-8','ignore')
    plaintext_output = "The ID of the recognized person is ".encode('utf-8','ignore') + plaintext_output + " - server".encode('utf-8','ignore')
    self.write_output('outfileServer', plaintext_output)

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
  app.run(host = '0.0.0.0', port = 5000, debug = DEBUG)