from people_counter.simple_classes import InputSource


class InputFrame:

    def __init__(self, frame, input_source: InputSource, time_stamp):
        self.frame = frame
        self.inputSource = input_source
        self.timeStamp = time_stamp

    def invert_bgr(self):
        """
        convert frame from BGR to RGB (openCV uses BGR)
        :return:
        """
        self.frame = self.frame[:, :, ::-1]
