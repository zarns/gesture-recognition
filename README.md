# gesture-recognition
Webcam + Machine Learning = Mouse 2.0

[![platform](https://img.shields.io/badge/platform-windows-green.svg)](https://github.com/zarns/gesture-recognition)
[![Awesome](https://cdn.jsdelivr.net/gh/sindresorhus/awesome@d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/sindresorhus/awesome#readme)

## Demo

![Demo](demo/demo.gif)

## Instructions

* Dominant Hand
  * V-Gesture/Bunny-Gesture to move mouse around screen
    * Left finger squeeze for `left-click`
    * Right finger squeeze for `right-click`
  * Claw-Gesture to `click and drag`
  * Pinch-Gesture
    * Move horizontally for `display brightness control`
    * Move vertically for `volume control`
* Non-Dominant Hand
  * Pinch-Gesture to `scroll` either horizontally or vertically

```bash 
python main.py
```

## Requirements

* [MediaPipe](https://mediapipe.dev/)
* [OpenCV](http://opencv.org)
* [pynput](https://pypi.org/project/pynput/)
* [pyautogui](https://pypi.org/project/PyAutoGUI/)
* [NumPy](https://numpy.org/)
* [Conda](https://docs.conda.io/en/latest/) is your friend

![MediaPipe](https://mediapipe.dev/images/mediapipe_small.png)
