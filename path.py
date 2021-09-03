import cv2


def draw_path(frame, point1, point2, color, width):
    side_line = []
    """
    (0, 0)------------l1----------(frame.shape[1], 0)
       |                                |
       |                                |
       |                                |
       l4                               l2
       |                                |
       |                                |
       |                                |
    (0, frame.shape[0])----l3----(frame.shape[1], frame.shape[0])
    """
    if point1[0] != point2[0] and point1[1] != point2[1]:
        dydx = float((point2[1] - point1[1]) / (point2[0] - point1[0]))

        b = point1[1] - dydx*point1[0]
        l1_x = int(-b/dydx)  # x = -b/a, y = 0
        l2_y = int(dydx*frame.shape[1] + b)  # y = ax + b, x = frame.
        l3_x = int((frame.shape[0] - b) / dydx)  # x = (y-b)/a
        l4_y = int(b)  # y = ax + b
        if point1[0] > point2[0]:
            if point1[1] < point2[1]:  # left buttom
                if l3_x >= 0:
                    side_line = [int(l3_x), frame.shape[0]]
                if l4_y <= frame.shape[0]:
                    side_line = [0, int(l4_y)]
            elif point1[1] > point2[1]:  # left top
                if l1_x >= 0:
                    side_line = [int(l1_x), 0]
                if l4_y >= 0:
                    side_line = [0, int(l4_y)]
        elif point1[0] < point2[0]:
            if point1[1] < point2[1]:  # right buttom
                if l3_x <= frame.shape[1]:
                    side_line = [int(l3_x), frame.shape[0]]
                if l2_y <= frame.shape[0]:
                    side_line = [frame.shape[1], int(l2_y)]
            if point1[1] > point2[1]:  # right top
                if l1_x <= frame.shape[1]:
                    side_line = [int(l1_x), 0]
                if l2_y >= 0:
                    side_line = [frame.shape[1], int(l2_y)]
    else:
        if point1[0] == point2[0]:
            if point1[1] > point2[1]:
                side_line = [point1[0], 0]
            else:
                side_line = [point1[0], frame.shape[0]]
        elif point1[1] == point2[1]:
            if point1[0] > point2[0]:
                side_line = [0, point1[1]]
            else:
                side_line = [frame.shape[1], point1[1]]

    if len(side_line) == 2:
        cv2.line(frame, [point1[0], point1[1]], side_line, color, width)


def draw_reflect(frame, dydx, point1):
    side_line = []
    """
    (0, 0)------------l1----------(frame.shape[1], 0)
       |                                |
       |                                |
       |                                |
       l4                               l2
       |                                |
       |                                |
       |                                |
    (0, frame.shape[0])----l3----(frame.shape[1], frame.shape[0])
    """

    b = point1[1] - dydx*point1[0]
    l1_x = int(-b/dydx)  # x = -b/a, y = 0
    l2_y = int(dydx*frame.shape[1] + b)  # y = ax + b, x = frame.shape[1]
    l3_x = int((frame.shape[0] - b) / dydx)  # x = (y-b)/a
    l4_y = int(b)  # y = ax + b
    if point1[0] == 0:  # at l4
        if l1_x >= 0 and l1_x <= frame.shape[1]:
            side_line = [l1_x, 0]
        if l2_y >= 0 and l2_y <= frame.shape[0]:
            side_line = [frame.shape[1], l2_y]
        if l3_x >= 0 and l3_x <= frame.shape[1]:
            side_line = [l3_x, frame.shape[0]]
    if point1[0] == frame.shape[1]:  # at l2
        if l1_x >= 0 and l1_x <= frame.shape[1]:
            side_line = [l1_x, 0]
        if l3_x >= 0 and l3_x <= frame.shape[1]:
            side_line = [l3_x, frame.shape[0]]
        if l4_y >= 0 and l4_y <= frame.shape[0]:
            side_line = [0, l4_y]
    if point1[1] == 0:  # at l1
        if l2_y >= 0 and l2_y <= frame.shape[0]:
            side_line = [frame.shape[1], l2_y]
        if l3_x >= 0 and l3_x <= frame.shape[1]:
            side_line = [l3_x, frame.shape[0]]
        if l4_y >= 0 and l4_y <= frame.shape[0]:
            side_line = [0, l4_y]
    if point1[1] == frame.shape[0]:  # at l3
        if l1_x >= 0 and l1_x <= frame.shape[1]:
            side_line = [l1_x, 0]
        if l2_y >= 0 and l2_y <= frame.shape[0]:
            side_line = [frame.shape[1], l2_y]
        if l4_y >= 0 and l4_y <= frame.shape[0]:
            side_line = [0, l4_y]

    if len(side_line) == 2:
        cv2.line(frame, [point1[0], point1[1]], side_line, (0, 0, 0), 3)

    return side_line[0], side_line[1]
