from controller import *
import cv2
import mediapipe as mp
from google.protobuf.json_format import MessageToDict
from hand_data import HandData as Hd

mp_draw_util = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands


# noinspection PyTypeChecker
class WebcamMouse:
    """
    Main entrypoint. Utilizes MediaPipe to extract hand features and gestures.
    Recognizes and represents hand states as 'HandPrint' objects.
    Delegates recognized gestures to 'Controller' to control Windows UI.

    Attributes
    ----------
    cap : 'Capture' object obtained from cv2, for capturing video frames.
    camera_width : int
        Height in pixels of obtained frames from webcam.
    camera_width : int
        Width in pixels of obtained frames from webcam.
    major_handprint : 'HandPrint' Object.
        object representing dominant/major hand.
    minor_handprint : 'HandPrint' Object.
        object representing non-dominant/minor hand.
    right_hand_dominant : bool
        True if right hand is dominant hand, otherwise False.
    """
    cap = None
    camera_height = None
    camera_width = None
    major_handprint = None
    minor_handprint = None
    right_hand_dominant = True

    def __init__(self):
        """Defines class attributes."""
        WebcamMouse.cap = cv2.VideoCapture(0)
        WebcamMouse.camera_height = WebcamMouse.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        WebcamMouse.camera_width = WebcamMouse.cap.get(cv2.CAP_PROP_FRAME_WIDTH)

    @staticmethod
    def classify_hands(results):
        """
        sets 'major_handprint', 'minor_handprint' with hand objects returned from
        MediaPipe. Dominant/Major hand assigned according to 'right_hand_dominant'.
        """

        left, right = None, None
        try:
            handedness_dict0 = MessageToDict(results.multi_handedness[0])
            if handedness_dict0['classification'][0]['label'] == 'Right':
                right = results.multi_hand_landmarks[0]
            else:
                left = results.multi_hand_landmarks[0]
        except:
            pass

        try:
            handedness_dict1 = MessageToDict(results.multi_handedness[1])
            if handedness_dict1['classification'][0]['label'] == 'Right':
                right = results.multi_hand_landmarks[1]
            else:
                left = results.multi_hand_landmarks[1]
        except:
            pass

        if WebcamMouse.right_hand_dominant:
            WebcamMouse.major_handprint = right
            WebcamMouse.minor_handprint = left
        else:
            WebcamMouse.major_handprint = left
            WebcamMouse.minor_handprint = right

    @staticmethod
    def start():
        """
        Captures video frame, obtains landmarks from MediaPipe and
        passes them to 'hand_major' and 'hand_minor' for UI control.
        """

        hand_major = HandPrint(1)
        hand_minor = HandPrint(0)

        with mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
            while WebcamMouse.cap.isOpened():
                success, image = WebcamMouse.cap.read()

                if not success:
                    print("WebcamMouse.cap.read() failed. Ignoring frame.")
                    continue

                image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                results = hands.process(image)

                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                if results.multi_hand_landmarks:
                    WebcamMouse.classify_hands(results)
                    hand_major.update_hand_result(WebcamMouse.major_handprint)
                    hand_minor.update_hand_result(WebcamMouse.minor_handprint)

                    hand_major.set_finger_state()
                    hand_minor.set_finger_state()
                    gesture_type = hand_minor.get_gesture()

                    if gesture_type == Hd.PINCH_MINOR:
                        Controller.handle_controls(gesture_type, hand_minor.hand_result)
                    else:
                        gesture_type = hand_major.get_gesture()
                        Controller.handle_controls(gesture_type, hand_major.hand_result)

                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_draw_util.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                else:
                    Controller.prev_hand = None
                cv2.imshow('Gesture Controller', image)
                if cv2.waitKey(5) & 0xFF == 13:
                    break
        WebcamMouse.cap.release()
        cv2.destroyAllWindows()
