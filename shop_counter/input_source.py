from enum import Enum


class ObjectDirection(Enum):
    ENTERING = 0
    EXITING = 1


class InputSource:
    def __init__(self, camera_id: str, location: str, monitored_direction: ObjectDirection):
        self.cameraId = camera_id
        self.location = location
        self.monitoredDirection = monitored_direction
