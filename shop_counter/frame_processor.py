import face_recognition
import numpy as np
from shop_counter.input_source import InputSource
from shop_counter.input_frame import InputFrame
from shop_counter.face_detection_event import FaceDetectionEvent
from shop_counter.face_detection_stats import FaceDetectionStats


class FrameProcessor:

    eventsById = {}

    DEBOUNCE_TIME_MS = 300000

    def __init__(self, source: InputSource):
        self.source = source

    def process(self, frame: InputFrame):
        events = []
        # Find all the faces and face encodings in the current frame of video
        # convert frame from BGR to RGB
        rgb_frame = frame.frame[:, :, ::-1]

        # apply faceDetection algorithm
        face_locations = face_recognition.face_locations(rgb_frame)
        print("I found {} face(s) in this photograph.".format(len(face_locations)))
        face_encodings = face_recognition.face_encodings(frame.frame, face_locations)

        # append face detected to lastEvent list
        for index, face_encoding in enumerate(face_encodings):
            ev = FaceDetectionEvent.create_event(face_locations[index],
                                                 face_encoding, self.source)

            filtered_event = self.process_single_event(ev)
            if filtered_event is not None:
                events.append(filtered_event)
                
        return events

    def process_single_event(self, ev: FaceDetectionEvent):
        # Se una faccia appare per la prima volta, non viene registrata.
        # Solo quando l'encoding appare N volte.
        # Secondo me questo filtro e' troppo rischioso. Se la telecamera lavora ad
        # un frame rate basso oppure
        # risulta poco efficiente rischiamo di perdere clienti
        # io metterei invece un filtro che se lo stessa faccia appare a distanza da
        # N secondi dal "primo" rilevamento
        # non la considero un nuovo evento. Il filtro si resetta quando passano
        # N secondi senza che quella faccia sia
        # stata rilevata nel campo visivo

        # we record events by encodings
        if ev.id in self.eventsById:
            return self.__process_event_with_id_already_present_in_history(ev)
        else:
            recorded_encodings = []
            for id, fds in self.eventsById.items():
                recorded_encodings.append(fds.encoding)

            matches = face_recognition.compare_faces(recorded_encodings, ev.encoding, 0.7)
            matched_indexes = [i for i in range(len(matches)) if matches[i]]

            # encoding match an old encoding. Use the encoding present in archive
            if len(matched_indexes) > 0:
                ev.replace_enconding(recorded_encodings[matched_indexes[0]])
                return self.__process_event_with_id_already_present_in_history(ev)
            else:
                # not present in stats. Initialize stats
                self.eventsById[ev.id] = FaceDetectionStats(ev.timestamp,ev.encoding,1)
                np.save("./encodings/" + ev.id, ev.encoding)
                return ev

    def __process_event_with_id_already_present_in_history(self, ev):
        fds: FaceDetectionStats = self.eventsById[ev.id]
        fds.nOccurencesSinceFirstDetTime += 1
        # check date time
        delta_ms = ev.timestamp - fds.firstDetTime
        # pass enough time since first detection. I can retrigger event
        if delta_ms > self.DEBOUNCE_TIME_MS:
            # reset stats starting from now
            fds.firstDetTime = ev.timestamp
            fds.nOccurencesSinceFirstDetTime = 1
            return ev
        else:

            # event is dropped because is to close to the previous one
            return None
