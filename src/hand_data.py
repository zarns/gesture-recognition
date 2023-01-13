from dataclasses import dataclass


@dataclass
class HandData:
    """
    Data class for hand recognition int mappings.
    Values are not arbitrary, they correspond to landmarks defined by MediaPipe
    """
    FIST = int(0)
    PINKY = int(1)
    RING = int(2)
    MID = int(4)
    LAST3 = int(7)
    INDEX = int(8)
    FIRST2 = int(12)
    LAST4 = int(15)
    THUMB = int(16)
    PALM = int(31)

    # Extra Mappings
    V_GEST = int(33)
    TWO_FINGER_CLOSED = int(34)
    PINCH_MAJOR = int(35)
    PINCH_MINOR = int(36)
