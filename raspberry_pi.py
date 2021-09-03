from imutils.perspective import four_point_transform
import base64
import requests
import cv2
import numpy
import os
import configparser


cfgpath = os.path.abspath('.') + "/config.ini"

config = configparser.ConfigParser()
config.read(cfgpath)


def mouse_click(event, x, y, flags, para):
    global four_points
    if event == cv2.EVENT_LBUTTONDOWN and len(four_points) < 4:
        print([x, y])
        four_points.append([x, y])
    elif event == cv2.EVENT_LBUTTONDOWN and len(four_points) == 4:
        four_points = []


video_file = './video/video1.mp4'
cap = cv2.VideoCapture(video_file)
# cap = cv2.VideoCapture(0)

four_points = [[437, 54], [909, 25], [1079, 898], [212, 911]]

cv2.namedWindow("origin")
cv2.setMouseCallback("origin", mouse_click)

while cap.isOpened():
    ret, frame = cap.read()
    if ret:
        if (len(four_points) == 4):
            frame = four_point_transform(frame, numpy.array(four_points))
        cv2.imshow("origin", frame)

        retval, buffer = cv2.imencode(".png", frame)
        jpg_as_text = base64.b64encode(buffer)
        send_data = {}
        send_data["image-64"] = str(jpg_as_text.decode("utf-8"))
        try:
            r = requests.post(
                "http://" + config["API"]["IP"] + ":" + config["API"]["PORT"] + "/post_img", json=send_data, timeout=0.03)
        except:
            pass

        if cv2.waitKey(1) == ord("q"):
            break
    else:
        cap = cv2.VideoCapture(video_file)
