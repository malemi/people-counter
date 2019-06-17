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
import face_det_event
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


url = 'http://192.168.4.10:8080/video/mjpeg'
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

startMjpegClient()

images_path = "./images/"
images = []
known_face_names = []
# write the encodings of known images

for d in listdir(images_path):
    if d[0] == '.':
        continue
# Load known pictures and name
    path = images_path + d + "/"
    for image in listdir(path):
        if image[0] == '.':
            continue
        known_face_names.append(d)
        images.append(face_recognition.load_image_file(path + "/" + image))
        
# encode this pictures and save the encoding
encoding_path = "./encodings/"
for i,name in enumerate(known_face_names):
    try:
        mkdir(encoding_path + name)
    except FileExistsError:
        shutil.rmtree(encoding_path + name)
        mkdir(encoding_path + name)
    enc = face_recognition.face_encodings(images[i])[0]
    np.save(encoding_path + name + "/" + str(abs(hash(str(enc)))), enc)


# Fill known_face_encodings with all encodings in the 
# encodings directory (which has all images from famous
# people and from past customers - if it's not from scratch)

seen_face_encodings = []
seen_face_names = []
for name in  listdir(encoding_path):
    if name[0] == '.':
        continue    
    for enc in listdir(encoding_path + name):
        if enc[0] == '.':
            continue        
        seen_face_encodings.append(np.load((encoding_path + name + "/" + enc)))
        seen_face_names.append(name)

assert(len(seen_face_names) == len(seen_face_encodings))
        
# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

#while (video_capture.isOpened()):
    # Grab a single frame of video
#    ret, frame = video_capture.read()
while True:

    currentRawFrame = getMjpegFrame()
    inputFrame = InputFrame(currentRawFrame,source,time.time() * 1000)
    # Only process every other frame of video to save time
    if process_this_frame:
        events = processor.process(inputFrame)

        face_names = []
        for index, ev in enumerate(events):


            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(seen_face_encodings, ev.encoding)
            name = str(uuid.uuid1())

            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            
            face_distances = face_recognition.face_distance(seen_face_encodings, ev.encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = seen_face_names[best_match_index]
            else:
                 mkdir(encoding_path + name)
                 np.save(encoding_path + name + "/" + str(abs(hash(str(ev.encoding)))), ev.encoding)
                 seen_face_names.append(name)
                 seen_face_encodings.append(face_encoding)

            face_names.append(name)

    process_this_frame = not process_this_frame


    # Display the results
    for ev in events:
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top = ev.location[0]
        right = ev.location[1]
        bottom = ev.location[2]
        left = ev.location[3]

        top *= 1
        right *= 1
        bottom *= 1
        left *= 1

        # Draw a box around the face
        cv2.rectangle(currentRawFrame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(currentRawFrame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(currentRawFrame,  ev.name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', currentRawFrame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
#video_capture.release()
cv2.destroyAllWindows()
