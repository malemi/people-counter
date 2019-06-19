import face_recognition
import cv2
import numpy as np
from os import listdir, rmdir, mkdir
import uuid
import shutil
import sys
from input_source import InputSource
from input_source import ObjectDirection
from input_frame import InputFrame
from frame_processor import FrameProcessor
from face_det_event import FaceDetEvent
from mjpeg.client import MJPEGClient
import time

# TODOs
# Se una faccia appare per la prima volta, non viene registrata. Solo quando l'encoding appare N volte.
# Se c'e` una faccia in una posizione, e il fotogramma dopo ne appare un'altra nella stessa posizione, non viene registrata.


# This is a demo of running face recognition on live video from your webcam. It's a little more complicated than the
# other example, but it includes some basic performance tweaks to make things run a lot faster:
#   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
#   2. Only detect faces in every other frame of video.

# PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
# OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
# specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

# Get a reference to webcam #0 (the default one)
# video_capture = cv2.VideoCapture(sys.argv[1])


url = 'http://192.168.4.10:8080/video/mjpeg'  #applicativo android camon
#url = 'http://192.168.4.2:8000/camera/mjpeg'  #applicativo pc cam2web from code project
source = InputSource("Cam1","Locale",ObjectDirection.ENTERING)
client = MJPEGClient(url)
processor = FrameProcessor(source)
bufs = []

def startMjpegClient():
    # Allocate memory buffers for frames
    bufs = client.request_buffers(1000000, 50)
    for b in bufs:
        client.enqueue_buffer(b)
    # Start the client in a background thread
    client.start()

def getMjpegFrame(resize_factor = 1.0):
    #fetch jpeg frame from client queue
    buf = client.dequeue_buffer()
    jpegData = buf.data[:buf.used]
    x = np.frombuffer(jpegData, dtype='uint8')
    #decode jpeg
    frame  = cv2.imdecode(x, 1)
    client.enqueue_buffer(buf)

    if resize_factor == 1.0:
        return frame
    else:
        small_frame = cv2.resize(frame, (0, 0), fx=resize_factor, fy=resize_factor)
        return small_frame


def drawOverlay(cvFrame, ev:FaceDetEvent):
    top = ev.boundingRect.y
    right = ev.boundingRect.x + ev.boundingRect.w
    bottom = ev.boundingRect.y + ev.boundingRect.h
    left = ev.boundingRect.x

    top *= 1
    right *= 1
    bottom *= 1
    left *= 1

    # Draw a box around the face
    cv2.rectangle(cvFrame, (left, top), (right, bottom), (0, 0, 255), 2)

    # Draw a label with a name below the face
    cv2.rectangle(cvFrame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(cvFrame, ev.name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)


startMjpegClient()

f = open("face_detected.log","a+")

#while (video_capture.isOpened()):
    # Grab a single frame of video
#    ret, frame = video_capture.read()
while True:

    currentRawFrame = getMjpegFrame()
    inputFrame = InputFrame(currentRawFrame,source,time.time() * 1000)
    # Only process every other frame of video to save time
    events = processor.process(inputFrame)

    face_names = []
    for index, ev in enumerate(events):

        print(ev.toCsv())
        f.write(ev.toCsv()+"\n")
        f.flush()




    # Display the results
    #for ev in events:
    #    drawOverlay(currentRawFrame,ev)

    # Display the resulting image
    #cv2.imshow('Video', currentRawFrame)

    # Hit 'q' on the keyboard to quit!
    #if cv2.waitKey(1) & 0xFF == ord('q'):
    #    break


#video_capture.release()
cv2.destroyAllWindows()
