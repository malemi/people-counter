
class FaceDetectionStats:
    def __init__(self, first_det_time: int, encoding,
                 n_occurences_since_first_det_time: int):
        self.encoding = encoding
        self.firstDetTime = first_det_time
        self.nOccurencesSinceFirstDetTime = n_occurences_since_first_det_time

