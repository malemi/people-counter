from input_source import  InputSource
from input_frame import InputFrame
from face_det_event import FaceDetEvent
import face_recognition
class FrameProcessor:

    def __init__(self, source: InputSource):
        self.source = source


    def process(self,frame: InputFrame):
        events = []
        # Find all the faces and face encodings in the current frame of video
        # convert frame from BGR to RGB
        rgbFrame  = frame.frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgbFrame)
        print("I found {} face(s) in this photograph.".format(len(face_locations)))
        face_encodings = face_recognition.face_encodings(frame.frame, face_locations)
        for index, face_encoding in enumerate(face_encodings):
            ev = FaceDetEvent.createEvent(face_locations[index], face_encoding, self.source)
            events.append(ev)
        return events