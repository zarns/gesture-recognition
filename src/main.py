from webcam_mouse import WebcamMouse


def main():
    print("Building WebcamMouse Object")
    webcam_mouse = WebcamMouse()
    print("Say Cheese!")
    webcam_mouse.start()


if __name__ == "__main__":
    main()
