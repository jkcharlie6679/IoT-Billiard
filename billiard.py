import math
from typing import AnyStr
import numpy as np
import cv2
from path import draw_path

balls = [[893, 695]]
cue_ball = [651, 442]
mouse = [0, 0]
cue = [[0, 0], [0, 0]]
ball_radis = 25
zero = 0.0000000001


def mouse_click(event, x, y, flags, para):
    global balls
    global mouse
    mouse = [x, y]
    if event == cv2.EVENT_LBUTTONDOWN:
        balls = [[x, y]]
        print("L", [x, y])
    if event == cv2.EVENT_RBUTTONDOWN:
        print("R", [x, y])


cv2.namedWindow("origin")
cv2.setMouseCallback("origin", mouse_click)


while True:
    frame = cv2.imread("./test.png")
    cv2.circle(frame, cue_ball, ball_radis, (255, 255, 255), -1)
    if mouse[0] - cue_ball[0] != 0:
        degree_cue_path = math.atan(
            (mouse[1] - cue_ball[1])/(mouse[0] - cue_ball[0]))
        if cue_ball[0] >= mouse[0]:
            cue[0] = [int(cue_ball[0] + math.cos(degree_cue_path) * 500),
                      int(cue_ball[1] + math.sin(degree_cue_path) * 500)]
            cue[1] = [int(cue_ball[0] + math.cos(degree_cue_path) * 45),
                      int(cue_ball[1] + math.sin(degree_cue_path) * 45)]
            cue_ball_path = [int(cue_ball[0] - math.cos(degree_cue_path) * ball_radis),
                             int(cue_ball[1] - math.sin(degree_cue_path) * ball_radis)]
        else:
            cue[0] = [int(cue_ball[0] - math.cos(degree_cue_path) * 500),
                      int(cue_ball[1] - math.sin(degree_cue_path) * 500)]
            cue[1] = [int(cue_ball[0] - math.cos(degree_cue_path) * 45),
                      int(cue_ball[1] - math.sin(degree_cue_path) * 45)]
            cue_ball_path = [int(cue_ball[0] + math.cos(degree_cue_path) * ball_radis),
                             int(cue_ball[1] + math.sin(degree_cue_path) * ball_radis)]

        cv2.line(frame, cue[0], cue[1], (35, 120, 90), 10)

        dydx_cue_path = (cue[0][1] - cue[1][1])/(cue[0][0] - cue[1][0])
        b_path = cue_ball[1] - dydx_cue_path*cue_ball[0]
        hit_ball = []
        ans = 0

        for ball in balls:
            length_2_path = abs(
                dydx_cue_path*ball[0] - ball[1] + b_path) / math.sqrt(dydx_cue_path**2 + 1)
            if length_2_path <= ball_radis*2:
                """
                filter ball show after cue have some bug
                """
                hit_ball = ball
                length_2_ball = math.sqrt((ball_radis*2)**2 - length_2_path**2)
                break

        if len(hit_ball) > 0:
            A = np.array([
                [-1, -dydx_cue_path],
                [dydx_cue_path, -1]
            ])
            B = np.array(
                [-hit_ball[0]-dydx_cue_path*hit_ball[1], -b_path]).reshape(2, 1)
            A_inv = np.linalg.inv(A)
            ans = A_inv.dot(B)
            if cue_ball[0] >= hit_ball[0]:
                cue_ball_hit_x_shift = math.cos(
                    degree_cue_path) * length_2_ball
                cue_ball_hit_y_shift = math.sin(
                    degree_cue_path) * length_2_ball
            elif cue_ball[0] < hit_ball[0]:
                cue_ball_hit_x_shift = - math.cos(
                    degree_cue_path) * length_2_ball
                cue_ball_hit_y_shift = - math.sin(
                    degree_cue_path) * length_2_ball
            if (cue_ball[0] < hit_ball[0] and math.sin(degree_cue_path) < 0 and cue_ball[1] < hit_ball[1] or
                    cue_ball[0] < hit_ball[0] and math.sin(degree_cue_path) > 0 and cue_ball[1] > hit_ball[1] or
                    cue_ball[0] >= hit_ball[0] and math.sin(degree_cue_path) > 0 and cue_ball[1] < hit_ball[1] or
                    cue_ball[0] >= hit_ball[0] and math.sin(degree_cue_path) < 0 and cue_ball[1] > hit_ball[1]):
                cue_ball_hit_x_shift = -cue_ball_hit_x_shift
                cue_ball_hit_y_shift = -cue_ball_hit_y_shift

            cue_ball_hit_position = [int(ans[0][0] + cue_ball_hit_x_shift),
                                     int(ans[1][0] + cue_ball_hit_y_shift)]

            touch_point = [int((cue_ball_hit_position[0]+hit_ball[0])/2),
                           int((cue_ball_hit_position[1]+hit_ball[1])/2)]
            """
            draw line
            """
            cv2.line(frame, cue_ball_path,
                     cue_ball_hit_position, (255, 255, 255), 1)
            cv2.circle(frame, cue_ball_hit_position,
                       ball_radis, (255, 255, 255), 2)
            draw_path(frame, touch_point, hit_ball, (255, 255, 255), 1)

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

            if abs(dydx_cue_path - dydx_hit) > 0.1:
                cv2.line(frame, cue_ball_hit_position,
                         cue_ball_rebound_path, (0, 0, 255), 2)
        else:
            draw_path(frame, cue_ball_path, mouse, (255, 255, 255), 1)
    """
    Draw ball and cue_ball
    """

    for ball in balls:
        cv2.circle(frame, ball, ball_radis, (0, 255, 0), -1)
        cv2.circle(frame, ball, 4, (34, 35, 255), -1)

    cv2.imshow("origin", frame)

    if cv2.waitKey(1) == ord("q"):
        break
