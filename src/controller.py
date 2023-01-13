from handprint import *
import pyautogui
from pynput.keyboard import Key
from pynput.keyboard import Controller as KeyboardController
import subprocess


class Controller:
    """
    Interface with Windows UI.

    Attributes
    ----------
    v_flag : bool
        true if V gesture is detected, allowing mouse movement.
    grab_flag : bool
        true if FIST gesture is detected, allowing drag movements.
    pinch_major_flag : bool
        true if PINCH gesture is detected through MAJOR/dominant hand,
        horizontal movement controls screen brightness.
        vertical movement controls volume.
    pinch_minor_flag : bool
        true if PINCH gesture is detected through MINOR hand,
        controls vertical AND horizontal scrolling.
    pinch_start_x : int
        x coordinate of hand landmark when pinch gesture is started.
    pinch_start_y : int
        y coordinate of hand landmark when pinch gesture is started.
    pinch_x_direction_flag : bool
        true if pinch gesture movement is along x-axis,
        otherwise false. Prevents unintentional diagonal scrolling.
    prev_pinch : int
        stores quantized magnitude of prev pinch gesture displacement, from
        starting position
    pinch : int
        stores quantized magnitude of pinch gesture displacement, from
        starting position
    frame_count : int
        stores no. of frames since 'pinch' is updated.
    prev_hand : tuple
        stores (x, y) coordinates of hand in previous frame.
    pinch_threshold : float
        step size for quantization of 'pinch'.
    """

    v_flag = False
    grab_flag = False
    pinch_major_flag = False
    pinch_minor_flag = False
    pinch_start_x = None
    pinch_start_y = None
    pinch_x_direction_flag = None
    prev_pinch = 0
    pinch = 0
    frame_count = 0
    prev_hand = None
    pinch_threshold = 0.3
    keyboard_controller = KeyboardController()

    @staticmethod
    def get_pinch_y(hand_result):
        """
        Returns distance between starting pinch y coord and current hand position y coord.
        """
        dist = round((Controller.pinch_start_y - hand_result.landmark[8].y) * 10, 1)
        return dist

    @staticmethod
    def get_pinch_x(hand_result):
        """
        Returns distance between starting pinch x coord and current hand position x coord.
        """
        dist = round((hand_result.landmark[8].x - Controller.pinch_start_x) * 10, 1)
        return dist

    @staticmethod
    def change_screen_brightness():
        """
        Sets system brightness based on 'Controller.pinch'.
        """
        def run_powershell_cmd(cmd):
            completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
            return completed

        # percent brightness of primary monitor
        new_brightness = int(50 + 20 * Controller.pinch)
        if new_brightness < 0:
            new_brightness = 0
        elif new_brightness > 100:
            new_brightness = 100

        command = "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1," + \
                  str(new_brightness) + ")"
        powershell_command = f"Write-Host {command}"
        success = run_powershell_cmd(powershell_command)
        if not success:
            print("Failed to change_screen_brightness.")

    @staticmethod
    def change_system_volume():
        """
        Increases/decreases system volume based on 'Controller.pinch'.
        """
        vol_change = Controller.pinch
        if vol_change > 0:
            Controller.keyboard_controller.press(Key.media_volume_up)
            Controller.keyboard_controller.release(Key.media_volume_up)
        if vol_change < 0:
            Controller.keyboard_controller.press(Key.media_volume_down)
            Controller.keyboard_controller.release(Key.media_volume_down)

    @staticmethod
    def scroll_vertical():
        """
        Scrolls on screen vertically.
        """
        pyautogui.scroll(120 if Controller.pinch > 0.0 else -120)

    @staticmethod
    def scroll_horizontal():
        """
        Scrolls on screen horizontally.
        """
        pyautogui.keyDown('shift')
        pyautogui.keyDown('ctrl')
        pyautogui.scroll(-120 if Controller.pinch > 0.0 else 120)
        pyautogui.keyUp('ctrl')
        pyautogui.keyUp('shift')

    # Locate Hand to get Cursor Position
    # Stabilize cursor by Dampening
    @staticmethod
    def get_position(hand_result):
        """
        Returns coordinates of current hand position.

        Locates hand to get cursor position also stabilize cursor by
        dampening jerky motion of hand.

        Returns
        -------
        tuple(float, float)
        """
        point = 9
        position = [hand_result.landmark[point].x, hand_result.landmark[point].y]
        sx, sy = pyautogui.size()
        x_old, y_old = pyautogui.position()
        x = int(position[0] * sx)
        y = int(position[1] * sy)
        if Controller.prev_hand is None:
            Controller.prev_hand = x, y
        delta_x = x - Controller.prev_hand[0]
        delta_y = y - Controller.prev_hand[1]

        dist_squared = delta_x ** 2 + delta_y ** 2
        Controller.prev_hand = [x, y]

        if dist_squared <= 25:
            ratio = 0
        elif dist_squared <= 900:
            ratio = 0.07 * (dist_squared ** (1 / 2))
        else:
            ratio = 2.1
        x, y = x_old + delta_x * ratio, y_old + delta_y * ratio
        return x, y

    @staticmethod
    def pinch_control_init(hand_result):
        """
        Initializes attributes for pinch gesture.
        """
        Controller.pinch_start_x = hand_result.landmark[8].x
        Controller.pinch_start_y = hand_result.landmark[8].y
        Controller.pinch = 0
        Controller.prev_pinch = 0
        Controller.frame_count = 0

    # Hold final position for 5 frames to change status
    @staticmethod
    def pinch_control(hand_result, control_horizontal, control_vertical):
        """
        Calls 'controlHorizontal' or 'control_vertical' based on pinch flags,
        'frame_count' and sets 'pinch'.

        Parameters
        ----------
        hand_result : Object
            Landmarks obtained from MediaPipe.
        control_horizontal : Callable
            Callback function associated with horizontal pinch gesture.
        control_vertical : Callable
            Callback function associated with vertical pinch gesture.

        Returns
        -------
        None
        """
        if Controller.frame_count == 5:
            Controller.frame_count = 0
            Controller.pinch = Controller.prev_pinch

            if Controller.pinch_x_direction_flag:
                control_horizontal()  # x

            elif not Controller.pinch_x_direction_flag:
                control_vertical()  # y

        x_dist = Controller.get_pinch_x(hand_result)
        y_dist = Controller.get_pinch_y(hand_result)

        if abs(y_dist) > abs(x_dist) and abs(y_dist) > Controller.pinch_threshold:
            Controller.pinch_x_direction_flag = False
            if abs(Controller.prev_pinch - y_dist) < Controller.pinch_threshold:
                Controller.frame_count += 1
            else:
                Controller.prev_pinch = y_dist
                Controller.frame_count = 0

        elif abs(x_dist) > Controller.pinch_threshold:
            Controller.pinch_x_direction_flag = True
            if abs(Controller.prev_pinch - x_dist) < Controller.pinch_threshold:
                Controller.frame_count += 1
            else:
                Controller.prev_pinch = x_dist
                Controller.frame_count = 0

    @staticmethod
    def handle_controls(gesture, hand_result):
        """
        Interprets gestures and plugs commands into Windows UI APIs

        Parameters
        ----------
        gesture : int
            Represents a type of gesture. Integer mappings found in 'HandData'
        hand_result : Object
            Hand landmarks obtained from MediaPipe.
        """
        x, y = None, None
        if gesture != Hd.PALM:
            x, y = Controller.get_position(hand_result)

        # v_flag reset
        if gesture != Hd.FIST and Controller.grab_flag:
            Controller.grab_flag = False
            pyautogui.mouseUp(button="left")

        if gesture != Hd.PINCH_MAJOR and Controller.pinch_major_flag:
            Controller.pinch_major_flag = False

        if gesture != Hd.PINCH_MINOR and Controller.pinch_minor_flag:
            Controller.pinch_minor_flag = False

        # implementation
        if gesture == Hd.V_GEST:
            Controller.v_flag = True
            pyautogui.moveTo(x, y, duration=0.1)

        elif gesture == Hd.FIST:
            if not Controller.grab_flag:
                Controller.grab_flag = True
                pyautogui.mouseDown(button="left")
            pyautogui.moveTo(x, y, duration=0.1)

        elif gesture == Hd.MID and Controller.v_flag:
            pyautogui.click()
            Controller.v_flag = False

        elif gesture == Hd.INDEX and Controller.v_flag:
            pyautogui.click(button='right')
            Controller.v_flag = False

        elif gesture == Hd.TWO_FINGER_CLOSED and Controller.v_flag:
            pyautogui.doubleClick()
            Controller.v_flag = False

        elif gesture == Hd.PINCH_MINOR:
            if not Controller.pinch_minor_flag:
                Controller.pinch_control_init(hand_result)
                Controller.pinch_minor_flag = True
            Controller.pinch_control(hand_result, Controller.scroll_horizontal, Controller.scroll_vertical)

        elif gesture == Hd.PINCH_MAJOR:
            if not Controller.pinch_major_flag:
                Controller.pinch_control_init(hand_result)
                Controller.pinch_major_flag = True
            Controller.pinch_control(hand_result, Controller.change_screen_brightness, Controller.change_system_volume)
