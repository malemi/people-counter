from input_source import  InputSource

class InputFrame:

    def __init__(self,frame,inputSource:InputSource,timeStamp):
        self.frame = frame
        self.inputSource = inputSource
        self.timeStamp = timeStamp

