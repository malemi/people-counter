import cv2
import numpy as np
from shop_counter.input_source import InputSource
from shop_counter.input_source import ObjectDirection
from shop_counter.input_frame import InputFrame
from shop_counter.frame_processor import FrameProcessor
from shop_counter.face_detection_event import FaceDetectionEvent
from mjpeg.client import MJPEGClient
import time
from os import listdir, rmdir, mkdir
import face_recognition
import shutil

# TODOs
# Se una faccia appare per la prima volta, non viene registrata. Solo quando l'encoding appare N volte.
# Se c'e` una faccia in una posizione, e il fotogramma dopo ne
# appare un'altra nella stessa posizione, non viene registrata.

# This is a demo of running face recognition on live video from your webcam. It's a little more complicated than the
# other example, but it includes some basic performance tweaks to make things run a lot faster:
#   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
#   2. Only detect faces in every other frame of video.

# PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
# OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
# specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

# Get a reference to webcam #0 (the default one)
# video_capture = cv2.VideoCapture(sys.argv[1])


class Session:
    """
    Acquire streaming and analyze images
    """

    def __init__(self, url, source, encoding_path=None, images_path="./images/"):

        self.client = MJPEGClient(url)
        self.processor = FrameProcessor(source)
        self.bufs = []

        self.images_path = images_path
        self.images = []
        self.known_face_names = []

        self.encoding_path = encoding_path
        self.seen_face_encodings = []
        self.seen_face_names = []

    def load_known_faces(self):
        """Load images in the dir images_path into images and the
        name into known_face_names.
        Images are in directories with the name of person (so we can
        have more images per person)
        """
        for d in listdir(self.images_path):
            if d[0] == '.':
                continue
            # Load known pictures and name
            path = self.images_path + d + "/"
            for image in listdir(path):
                if image[0] == '.':
                    continue
                self.known_face_names.append(d)
                self.images.append(face_recognition.load_image_file(path + "/" + image))

        for i, name in enumerate(self.known_face_names):
            try:
                mkdir(self.encoding_path + name)
            except FileExistsError:
                shutil.rmtree(self.encoding_path + name)
                mkdir(self.encoding_path + name)
            enc = face_recognition.face_encodings(self.images[i])[0]
            np.save(self.encoding_path + name + "/" + str(abs(hash(str(enc)))), enc)

    def load_old_customers(self):
        """Fill known_face_encodings with all encodings in the
            encodings directory (which has all images from famous
            people and from past customers - if it's not from scratch)
        """

        for name in listdir(self.encoding_path):
            if name[0] == '.':
                continue
            for enc in listdir(self.encoding_path + name):
                if enc[0] == '.':
                    continue
                self.seen_face_encodings.append(np.load((self.encoding_path +
                                                         name + "/" + enc)))
                self.seen_face_names.append(name)
        assert (len(self.encoding_path) == len(self.seen_face_encodings))

    def start_mjpeg_client(self):
        # Allocate memory buffers for frames
        bufs = self.client.request_buffers(1000000, 50)
        for b in bufs:
            self.client.enqueue_buffer(b)
        # Start the client in a background thread
        self.client.start()

    def get_mjpeg_frame(self, resize_factor=1.0):
        # fetch jpeg frame from client queue
        buf = self.client.dequeue_buffer()
        jpeg_data = buf.data[:buf.used]
        x = np.frombuffer(jpeg_data, dtype='uint8')
        # decode jpeg
        frame = cv2.imdecode(x, 1)
        self.client.enqueue_buffer(buf)

        if resize_factor == 1.0:
            return frame
        else:
            small_frame = cv2.resize(frame, (0, 0), fx=resize_factor, fy=resize_factor)
            return small_frame

    @staticmethod
    def draw_overlay(cv_frame, ev: FaceDetectionEvent):
        top = ev.boundingRect.y
        right = ev.boundingRect.x + ev.boundingRect.w
        bottom = ev.boundingRect.y + ev.boundingRect.h
        left = ev.boundingRect.x

        top *= 1
        right *= 1
        bottom *= 1
        left *= 1

        # Draw a box around the face
        cv2.rectangle(cv_frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(cv_frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(cv_frame, ev.name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    def run(self):

        self.start_mjpeg_client()

        f = open("face_detected.log", "a+")

        # while (video_capture.isOpened()):
        # Grab a single frame of video
        #    ret, frame = video_capture.read()

        while True:

            current_raw_frame = self.get_mjpeg_frame()
            input_frame = InputFrame(current_raw_frame, source, time.time() * 1000)
            # Only process every other frame of video to save time
            events = self.processor.process(input_frame)

            face_names = []
            for index, ev in enumerate(events):

                print(ev.to_csv())
                f.write(ev.to_csv() + "\n")
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
        #cv2.destroyAllWindows()



url = 'http://192.168.1.74:8080/video/mjpeg'  #applicativo android camon
url = 'http://192.168.1.2:8080/video/mjpeg'  #applicativo android camon
#url = 'http://192.168.4.2:8000/camera/mjpeg'  #applicativo pc cam2web from code project
source = InputSource("Cam1", "Locale", ObjectDirection.ENTERING)

session = Session(url, source)

session.run()
