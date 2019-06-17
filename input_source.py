from enum import Enum

class ObjectDirection(Enum):
    ENTERING = 0
    EXITING  = 1

class InputSource:
    def __init__(self, cameraId: str, location: str, monitoredDirection: ObjectDirection):
        self.cameraId = cameraId
        self.location = location
        self.monitoredDirection = monitoredDirection