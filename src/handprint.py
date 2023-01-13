import numpy as np
from hand_data import HandData as Hd


class HandPrint:
    """
    Uses landmarks from MediaPipe to recognize and represent hand features.
    """

    def __init__(self, hand_label):
        """
        Constructor.

        Parameters
        ----------
            hand_label : int
                Dominant/Major hand represented by 1. Non-dominant/Minor hand represented by 0.
        """

        self.finger = 0
        self.active_gesture = Hd.PALM
        self.prev_gesture = Hd.PALM
        self.frame_count = 0
        self.hand_result = None
        self.hand_label = hand_label

    def update_hand_result(self, hand_result):
        self.hand_result = hand_result

    def get_signed_dist(self, points):
        """
        Calculates euclidean distance between landmarks. Sign representing vertical direction

        Parameters
        ----------
        points : list containing two elements of type list/tuple which represents
            landmark points.

        Returns
        -------
        float
        """
        point1 = np.array([self.hand_result.landmark[points[0]].x, self.hand_result.landmark[points[0]].y])
        point2 = np.array([self.hand_result.landmark[points[1]].x, self.hand_result.landmark[points[1]].y])
        dist = np.linalg.norm(point1 - point2)
        sign = np.sign(point2[1] - point1[1])
        return dist * sign

    def get_dist(self, points):
        """
        Returns euclidean distance between 'points'. Unsigned.

        Parameters
        ----------
        points : list containing two elements of type list/tuple representing landmark points.

        Returns
        -------
        float
        """
        dist = (self.hand_result.landmark[points[0]].x - self.hand_result.landmark[points[1]].x) ** 2
        dist += (self.hand_result.landmark[points[0]].y - self.hand_result.landmark[points[1]].y) ** 2
        dist = np.sqrt(dist)
        return dist

    def get_dz(self, points):
        """
        Returns difference on z-axis between 'points'. Unsigned.

        Parameters
        ----------
        points : list containing two elements of type list/tuple which represents
            landmark points.

        Returns
        -------
        float
        """
        return abs(self.hand_result.landmark[points[0]].z - self.hand_result.landmark[points[1]].z)

    def set_finger_state(self):
        """
        Set 'finger' openness state by triangulating fingertips, middle knuckles, base knuckles.

        Returns
        -------
        None
        """
        if self.hand_result is None:
            return

        points_list = [[8, 5, 0], [12, 9, 0], [16, 13, 0], [20, 17, 0]]
        self.finger = 0
        self.finger = self.finger | 0  # thumb
        for idx, points in enumerate(points_list):

            dist = self.get_signed_dist(points[:2])
            dist2 = self.get_signed_dist(points[1:])

            try:
                ratio = round(dist / dist2, 1)
            except:
                ratio = round(dist / 0.01, 1)

            self.finger = self.finger << 1
            if ratio > 0.5:
                self.finger = self.finger | 1

    def get_gesture(self):
        """
        Returns int representing gesture corresponding to 'Hd'.
        sets 'frame_count', 'active_gesture', 'prev_gesture'.

        Returns
        -------
        int
        """
        if self.hand_result is None:
            return Hd.PALM

        if self.finger in [Hd.LAST3, Hd.LAST4] and self.get_dist([Hd.INDEX, Hd.MID]) < 0.05:
            if self.hand_label == 0:
                current_gesture = Hd.PINCH_MINOR
            else:
                current_gesture = Hd.PINCH_MAJOR

        elif Hd.FIRST2 == self.finger:
            point = [[Hd.INDEX, Hd.FIRST2], [5, 9]]
            dist1 = self.get_dist(point[0])
            dist2 = self.get_dist(point[1])
            ratio = dist1 / dist2
            if ratio > 1.7:
                current_gesture = Hd.V_GEST
            else:
                if self.get_dz([8, 12]) < 0.1:
                    current_gesture = Hd.TWO_FINGER_CLOSED
                else:
                    current_gesture = Hd.MID

        else:
            current_gesture = self.finger

        if current_gesture == self.prev_gesture:
            self.frame_count += 1
        else:
            self.frame_count = 0

        self.prev_gesture = current_gesture

        if self.frame_count > 4:
            self.active_gesture = current_gesture
        return self.active_gesture
