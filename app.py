from cuefinder import CueFinder
from ballfinder import red, yellow, white, blue, green, black
from path import draw_path
from flask import Flask, config, render_template, request
from flask_cors import cross_origin
from flask_socketio import SocketIO, emit
import json
import base64
import cv2
import numpy as np
import os
import configparser
import math


app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*")


frame_text = None
ball_text = None
cue_text = None


cfgpath = os.path.abspath('.') + "/config.ini"

config = configparser.ConfigParser()
config.read(cfgpath)


def detect_ball_color(frame):
    """
    use HSV to filter the ball by color
    """

    red_frame, red = redball.process(frame)

    yellow_frame, yellow = yellowball.process(frame)
    if len(yellow) != 0:
        red.append(yellow[0])
    ball_frame = cv2.bitwise_or(red_frame, yellow_frame)

    white_frame, white = whiteball.process(frame)
    if len(white) != 0:
        red.append(white[0])
    ball_frame = cv2.bitwise_or(ball_frame, white_frame)

    green_frame, green = greenball.process(frame)
    if len(green) != 0:
        red.append(green[0])
    ball_frame = cv2.bitwise_or(ball_frame, green_frame)

    blue_frame, blue = blueball.process(frame)
    if len(blue) != 0:
        red.append(blue[0])
    ball_frame = cv2.bitwise_or(ball_frame, blue_frame)

    black_frame, black = blackball.process(frame)
    if len(black) != 0:
        red.append(black[0])
    ball_frame = cv2.bitwise_or(ball_frame, black_frame)

    return ball_frame, red


@app.route("/")
def output():
    return render_template("index.html")


@app.route("/get_img", methods=["GET"])
@cross_origin()
def get_img():
    global frame_text
    global ball_text
    global cue_text
    data = {
        'frame': frame_text,
        'ball': ball_text,
        'cue': cue_text
    }
    return json.dumps(data)


@ app.route("/post_img", methods=["POST"])
@cross_origin()
def post_img():
    global frame_text
    global ball_text
    global cue_text

    get_json = request.json
    image_buffer = get_json['image-64']

    ball_radis = 10
    ball_smallest_area = 50
    cue_2_cue_ball_smallest = 1000000
    zero = 0.000000001
    img_data = base64.b64decode(image_buffer)
    nparr = np.frombuffer(img_data, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    """
    using ML to find the ball, and use the otsu to get the ball contours
    """
    balls = []
    ball_cascade = cv2.CascadeClassifier('./dataset/xml/cascade.xml')
    faces = ball_cascade.detectMultiScale(cv2.cvtColor(
        frame, cv2.COLOR_BGR2GRAY), maxSize=(40, 40), minSize=(20, 20))
    for (x, y, w, h) in faces:
        ret, ball_cap = cv2.threshold(cv2.cvtColor(frame[y:y+h, x:x+w], cv2.COLOR_BGR2GRAY), 0, 255,
                                      cv2.THRESH_BINARY+cv2.THRESH_OTSU)

        contours, hierarchy = cv2.findContours(
            ball_cap, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
        for data in contours:
            area = cv2.contourArea(data)
            if area < ball_smallest_area:
                continue
            M = cv2.moments(data)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.circle(frame, (x+cX, y+cY), 3, (34, 35, 255), -1)
            cv2.circle(frame, (x+cX, y+cY), ball_radis, (255, 255, 255), 1)
            balls.append([x+cX, y+cY])
    ball_frame = frame.copy()
    cue_frame, cue_detect = Cue.process(frame)

    """
    find the cue ball and cue direction
    """

    cue = []
    cue_ball = []
    if len(balls) > 0 and len(cue_detect) > 0 and len(cue_detect) < 3:
        """
        find the cue and cue ball
        """
        for ball in balls:
            l1 = (ball[0] - cue_detect[0][0])**2 + \
                (ball[1] - cue_detect[0][1])**2
            l2 = (ball[0] - cue_detect[1][0])**2 + \
                (ball[1] - cue_detect[1][1])**2
            if l1 < cue_2_cue_ball_smallest:
                cue_2_cue_ball_smallest = l1
                cue = [[cue_detect[1][0], cue_detect[1][1]],
                       [cue_detect[0][0], cue_detect[0][1]]]
                cue_ball = ball
            if l2 < cue_2_cue_ball_smallest:
                cue_2_cue_ball_smallest = l2
                cue = [[cue_detect[0][0], cue_detect[0][1]],
                       [cue_detect[1][0], cue_detect[1][1]]]
                cue_ball = ball
        balls = balls[:balls.index(cue_ball)] + balls[balls.index(cue_ball)+1:]

        """
        Find the hit ball
        """

        dydx_cue = (cue[0][1] - cue[1][1])/(cue[0][0] - cue[1][0])
        b_path = cue_ball[1] - dydx_cue*cue_ball[0]
        degree_cue = math.atan(dydx_cue)
        hit_ball = []
        cue_2_hit_ball_length = 300000
        ans = 0

        for ball in balls:
            length_2_path = abs(
                dydx_cue*ball[0] - ball[1] + b_path) / math.sqrt(dydx_cue**2 + 1)
            if length_2_path <= ball_radis*2:
                """
                filter ball show after cue have some bug
                """
                # if cue[0][0] > cue[1][0] and cue_ball[0] < ball[0]:
                #     continue
                # if cue[0][0] < cue[1][0] and cue_ball[0] > ball[0]:
                #     continue
                # if cue[0][1] > cue[1][1] and cue_ball[1] < ball[1]:
                #     continue
                # if cue[0][1] < cue[1][1] and cue_ball[1] > ball[1]:
                #     continue
                cue_2_hit_ball_length = math.sqrt(
                    (ball[0] - cue_ball[0])**2+(ball[1] - cue_ball[1])**2)
                if cue_2_hit_ball_length < cue_2_cue_ball_smallest:
                    cue_2_cue_ball_smallest = cue_2_cue_ball_smallest
                    hit_ball = ball
                    length_2_ball = math.sqrt(
                        (ball_radis*2)**2 - length_2_path**2)
                # break

        if len(hit_ball) > 0:
            """
            find the cue ball hit position
            """
            A = np.array([
                [-1, -dydx_cue],
                [dydx_cue, -1]
            ])
            B = np.array(
                [-hit_ball[0]-dydx_cue*hit_ball[1], -b_path]).reshape(2, 1)
            A_inv = np.linalg.inv(A)
            ans = A_inv.dot(B)

            if cue_ball[0] >= hit_ball[0]:
                cue_ball_hit_x_shift = math.cos(
                    degree_cue) * length_2_ball
                cue_ball_hit_y_shift = math.sin(
                    degree_cue) * length_2_ball
            elif cue_ball[0] < hit_ball[0]:
                cue_ball_hit_x_shift = - math.cos(
                    degree_cue) * length_2_ball
                cue_ball_hit_y_shift = - math.sin(
                    degree_cue) * length_2_ball
            if (cue_ball[0] < hit_ball[0] and math.sin(degree_cue) < 0 and cue_ball[1] < hit_ball[1] or
                    cue_ball[0] < hit_ball[0] and math.sin(degree_cue) > 0 and cue_ball[1] > hit_ball[1] or
                    cue_ball[0] >= hit_ball[0] and math.sin(degree_cue) > 0 and cue_ball[1] < hit_ball[1] or
                    cue_ball[0] >= hit_ball[0] and math.sin(degree_cue) < 0 and cue_ball[1] > hit_ball[1]):
                cue_ball_hit_x_shift = -cue_ball_hit_x_shift
                cue_ball_hit_y_shift = -cue_ball_hit_y_shift

            cue_ball_hit_position = [int(ans[0][0] + cue_ball_hit_x_shift),
                                     int(ans[1][0] + cue_ball_hit_y_shift)]
            touch_point = [int((cue_ball_hit_position[0]+hit_ball[0])/2),
                           int((cue_ball_hit_position[1]+hit_ball[1])/2)]
            """
            find the cue ball path
            """
            if cue_ball[0] >= cue_ball_hit_position[0]:
                cue_ball_path = [int(cue_ball[0] - math.cos(degree_cue) * ball_radis),
                                 int(cue_ball[1] - math.sin(degree_cue) * ball_radis)]
            else:
                cue_ball_path = [int(cue_ball[0] + math.cos(degree_cue) * ball_radis),
                                 int(cue_ball[1] + math.sin(degree_cue) * ball_radis)]
            """
            draw line
            """
            cv2.line(frame, cue_ball_path,
                     cue_ball_hit_position, (255, 255, 255), 1)
            cv2.circle(frame, cue_ball_hit_position,
                       ball_radis, (255, 255, 255), 2)
            draw_path(frame, touch_point, hit_ball, (255, 255, 255), 1)
            """
            cue rebound
            """
            touch_ball1_minus_hit1 = touch_point[1] - hit_ball[1]

            if touch_ball1_minus_hit1 == 0:
                touch_ball1_minus_hit1 = zero

            dydx_cue_rebound = - \
                (touch_point[0] - hit_ball[0]) / touch_ball1_minus_hit1

            degree_cue_rebound_path = math.atan(dydx_cue_rebound)

            cue_ball_minus_hit = cue_ball[0] - hit_ball[0]
            if cue_ball_minus_hit == 0:
                cue_ball_minus_hit = zero

            dydx_cue_hit = (cue_ball[1]-hit_ball[1]) / cue_ball_minus_hit
            b_cue_hit = cue_ball[1]-dydx_cue_hit*cue_ball[0]

            cue_rebound_directtion = dydx_cue_hit * \
                cue_ball_hit_position[0] - \
                cue_ball_hit_position[1] + b_cue_hit

            touch_ball0_minus_hit0 = touch_point[0]-hit_ball[0]
            if touch_ball0_minus_hit0 == 0:
                touch_ball0_minus_hit0 = zero

            dydx_hit = (touch_point[1]-hit_ball[1]) / touch_ball0_minus_hit0

            if cue_ball[0] < hit_ball[0] and cue_ball[1] > hit_ball[1]:
                if cue_rebound_directtion > 0:
                    if dydx_hit < 0:
                        cue_ball_rebound_x_shitf = - \
                            abs(math.cos(degree_cue_rebound_path)) * 50
                        cue_ball_rebound_y_shitf = - \
                            abs(math.sin(degree_cue_rebound_path)) * 50
                    else:
                        cue_ball_rebound_x_shitf = abs(
                            math.cos(degree_cue_rebound_path)) * 50
                        cue_ball_rebound_y_shitf = - \
                            abs(math.sin(degree_cue_rebound_path)) * 50
                else:
                    if dydx_hit < 0:
                        cue_ball_rebound_x_shitf = abs(
                            math.cos(degree_cue_rebound_path)) * 50
                        cue_ball_rebound_y_shitf = abs(
                            math.sin(degree_cue_rebound_path)) * 50
                    else:
                        cue_ball_rebound_x_shitf = abs(
                            math.cos(degree_cue_rebound_path)) * 50
                        cue_ball_rebound_y_shitf = - \
                            abs(math.sin(degree_cue_rebound_path)) * 50
            elif cue_ball[0] > hit_ball[0] and cue_ball[1] > hit_ball[1]:
                if cue_rebound_directtion > 0:
                    if dydx_hit < 0:
                        cue_ball_rebound_x_shitf = - \
                            abs(math.cos(degree_cue_rebound_path)) * 50
                        cue_ball_rebound_y_shitf = - \
                            abs(math.sin(degree_cue_rebound_path)) * 50
                    else:
                        cue_ball_rebound_x_shitf = + \
                            abs(math.cos(degree_cue_rebound_path)) * 50
                        cue_ball_rebound_y_shitf = - \
                            abs(math.sin(degree_cue_rebound_path)) * 50
                else:
                    if dydx_hit < 0:
                        cue_ball_rebound_x_shitf = - \
                            abs(math.cos(degree_cue_rebound_path)) * 50
                        cue_ball_rebound_y_shitf = - \
                            abs(math.sin(degree_cue_rebound_path)) * 50
                    else:
                        cue_ball_rebound_x_shitf = - \
                            abs(math.cos(degree_cue_rebound_path)) * 50
                        cue_ball_rebound_y_shitf = abs(
                            math.sin(degree_cue_rebound_path)) * 50
            elif cue_ball[0] > hit_ball[0] and cue_ball[1] < hit_ball[1]:
                if cue_rebound_directtion > 0:
                    if dydx_hit < 0:
                        cue_ball_rebound_x_shitf = - \
                            abs(math.cos(degree_cue_rebound_path)) * 50
                        cue_ball_rebound_y_shitf = - \
                            abs(math.sin(degree_cue_rebound_path)) * 50
                    else:
                        cue_ball_rebound_x_shitf = - \
                            abs(math.cos(degree_cue_rebound_path)) * 50
                        cue_ball_rebound_y_shitf = abs(
                            math.sin(degree_cue_rebound_path)) * 50
                else:
                    if dydx_hit < 0:
                        cue_ball_rebound_x_shitf = abs(
                            math.cos(degree_cue_rebound_path)) * 50
                        cue_ball_rebound_y_shitf = abs(
                            math.sin(degree_cue_rebound_path)) * 50
                    else:
                        cue_ball_rebound_x_shitf = - \
                            abs(math.cos(degree_cue_rebound_path)) * 50
                        cue_ball_rebound_y_shitf = abs(
                            math.sin(degree_cue_rebound_path)) * 50
            elif cue_ball[0] < hit_ball[0] and cue_ball[1] < hit_ball[1]:
                if cue_rebound_directtion > 0:
                    if dydx_hit < 0:
                        cue_ball_rebound_x_shitf = abs(
                            math.cos(degree_cue_rebound_path)) * 50
                        cue_ball_rebound_y_shitf = abs(
                            math.sin(degree_cue_rebound_path)) * 50
                    else:
                        cue_ball_rebound_x_shitf = abs(
                            math.cos(degree_cue_rebound_path)) * 50
                        cue_ball_rebound_y_shitf = - \
                            abs(math.sin(degree_cue_rebound_path)) * 50
                else:
                    if dydx_hit < 0:
                        cue_ball_rebound_x_shitf = abs(
                            math.cos(degree_cue_rebound_path)) * 50
                        cue_ball_rebound_y_shitf = abs(
                            math.sin(degree_cue_rebound_path)) * 50
                    else:
                        cue_ball_rebound_x_shitf = - \
                            abs(math.cos(degree_cue_rebound_path)) * 50
                        cue_ball_rebound_y_shitf = abs(
                            math.sin(degree_cue_rebound_path)) * 50
            cue_ball_rebound_path = [int(cue_ball_hit_position[0] + cue_ball_rebound_x_shitf),
                                     int(cue_ball_hit_position[1] + cue_ball_rebound_y_shitf)]
            if abs(dydx_cue - dydx_hit) > 0.1:
                cv2.line(frame, cue_ball_hit_position,
                         cue_ball_rebound_path, (0, 0, 255), 2)
        else:
            draw_path(frame, cue[0], cue[1], (255, 255, 255), 1)

    retval_frame, buffer_frame = cv2.imencode(".png", frame)
    frame_text = str(base64.b64encode(buffer_frame).decode("utf-8"))

    retval_ball, buffer_ball = cv2.imencode(".png", ball_frame)
    ball_text = str(base64.b64encode(buffer_ball).decode("utf-8"))

    retval_cue, buffer_cue = cv2.imencode(".png", cue_frame)
    cue_text = str(base64.b64encode(buffer_cue).decode("utf-8"))

    data = {
        'frame': frame_text,
        'ball': ball_text,
        'cue': cue_text
    }

    socketio.emit('hoho', json.dumps(data))
    return "done"


if __name__ == "__main__":
    Cue = CueFinder()
    redball = red()
    yellowball = yellow()
    whiteball = white()
    blueball = blue()
    greenball = green()
    blackball = black()
    socketio.run(app, host=config["API"]["HOST"], debug=True)
