import datetime
import time
from input_source import  InputSource
import uuid
class FaceBoundingRect:
    def __init__(self, location):
        # relative face position inside image tuple in (top, right, bottom, left)
        top = location[0]
        right = location[1]
        bottom = location[2]
        left = location[3]
        self.x = left
        self.y = top
        self.w = right - left
        self.h = bottom - top

    def __str__(self):
        return "[" + str(self.x) + ":" + str(self.y) + "](" + str(self.w) + ":" + str(self.h) +")"
    def toCsv(self):
        return str(self.x) + "," + str(self.y) + "," + str(self.w) + "," + str(self.h)


class FaceDetEvent:

    def __init__(self, location, encoding, timestamp, inputSource: InputSource):
        # relative face position inside image tuple in (top, right, bottom, left)
        self.boundingRect = FaceBoundingRect(location)
        # binary data embedding the face features  128 double array Numpy
        self.encoding = encoding
        # time from epoch in ms
        self.timestamp = timestamp
        # camera string id
        self.inputSource = inputSource
        self.id = str(abs(hash(str(encoding))))
        self.name = str(uuid.uuid1())

    def __str__(self):
        dt = datetime.datetime.fromtimestamp(self.timestamp / 1000).strftime('%c')
        s = dt + ":Object " + self.inputSource.location + ":Pos  " + self.boundingRect
        return s

    def replaceEnconding(self,encoding):
        self.encoding = encoding
        self.id = str(abs(hash(str(encoding))))

    def toCsv(self):
        return str(int(self.timestamp)) + "," + self.id + "," + self.boundingRect.toCsv()  + "," + self.inputSource.location

    def createEvent(location, encoding, camera_id):
        return FaceDetEvent(location, encoding, time.time() * 1000, camera_id)
