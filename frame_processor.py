from input_source import  InputSource
from input_frame import InputFrame
from face_det_event import FaceDetEvent
import face_recognition


class FaceDetStats:
    def __init__(self, firstDetTime:int, nOccurencesSinceFirstDetTime:int):
        self.firstDetTime = firstDetTime
        self.nOccurencesSinceFirstDetTime = nOccurencesSinceFirstDetTime



class FrameProcessor:

    eventsById = {}

    DEBOUNCE_TIME_MS = 10000

    def __init__(self, source: InputSource):
        self.source = source


    def process(self,frame: InputFrame):
        events = []
        # Find all the faces and face encodings in the current frame of video
        # convert frame from BGR to RGB
        rgbFrame  = frame.frame[:, :, ::-1]

        #apply faceDetection algorithm
        face_locations = face_recognition.face_locations(rgbFrame)
        print("I found {} face(s) in this photograph.".format(len(face_locations)))
        face_encodings = face_recognition.face_encodings(frame.frame, face_locations)

        #append face detected to lastEvent list
        for index, face_encoding in enumerate(face_encodings):
            ev = FaceDetEvent.createEvent(face_locations[index], face_encoding, self.source)

            filteredEvent = self.processSingleEvent(ev)
            if filteredEvent is not None:
                events.append(filteredEvent)


        return events


    def processSingleEvent(self, ev: FaceDetEvent):
        # Se una faccia appare per la prima volta, non viene registrata. Solo quando l'encoding appare N volte.
        # Secondo me questo filtro e' troppo rischioso. Se la telecamera lavora ad un frame rate basso oppure
        # risulta poco efficiente rischiamo di perdere clienti
        # io metterei invece un filtro che se lo stessa faccia appare a distanza da N secondi dal "primo" rilevamento
        # non la considero un nuovo evento. Il filtro si resetta quando passano N secondi senza che quella faccia sia
        # stata rilevata nel campo visivo

        # we record events by encodings
        if ev.id in self.eventsById:
            #event is already in the history
            fds: FaceDetStats = self.eventsById[ev.id]
            fds.nOccurencesSinceFirstDetTime += 1
            #check date time
            delta_ms = ev.timestamp - fds.firstDetTime
            #pass enough time since first detection. I can retrigger event
            if delta_ms > self.DEBOUNCE_TIME_MS:
                #reset stats starting from now
                fds.firstDetTime = ev.timestamp
                fds.nOccurencesSinceFirstDetTime = 1
                return ev
            else:
                #event is dropped because is to close to the previous one
                return None

        else:
            #not present in stats. Initialize stats
            self.eventsById[ev.id] = FaceDetStats(ev.timestamp,1)
            return ev
