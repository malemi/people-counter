import datetime
import time
from input_source import  InputSource
import uuid
class FaceDetEvent:

    def __init__(self, location, encoding, timestamp, inputSource: InputSource):
        # relative face position inside image tuple in (top, right, bottom, left)
        self.location = location
        # binary data embedding the face features  128 double array Numpy
        self.encoding = encoding
        # time from epoch in ms
        self.timestamp = timestamp
        # camera string id
        self.inputSource = inputSource
        self.name = str(uuid.uuid1())

    def __str__(self):
        dt = datetime.datetime.fromtimestamp(self.timestamp / 1000).strftime('%c')
        s = dt + ":Object " + self.inputSource.location + ":Pos  " + self.location
        return s

    def createEvent(location, encoding, camera_id):
        return FaceDetEvent(location, encoding, time.time() * 1000, camera_id)
