import cv2
import numpy as np


class ball:
    def __init__(self):
        """
        Set value to filter the ball
        Dependent on the web cam resolutioin
        """
        self.filter_contours_min_area = 100
        self.filter_contours_min_perimeter = 0
        self.filter_contours_min_width = 0
        self.filter_contours_max_width = 40
        self.filter_contours_min_height = 0
        self.filter_contours_max_height = 40
        self.filter_contours_solidity = [85, 100.0]
        self.filter_contours_max_vertices = 1000000
        self.filter_contours_min_vertices = 0
        self.filter_contours_min_ratio = 0
        self.filter_contours_max_ratio = 1000

    def process(self, source):
        self.rgb_threshold_input = source
        self.hsv_threshold_output = self.__hsv_threshold(
            self.rgb_threshold_input
        )
        # return self.hsv_threshold_output
        self.find_contours_output = self.find_contours(
            self.hsv_threshold_output)

        return self.hsv_threshold_output, self.filter_contours(
            source,
            self.find_contours_output,
        )

    def __hsv_threshold(self, input):
        out = cv2.cvtColor(input, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(
            out, (self.hsv_threshold_hue[0], self.hsv_threshold_saturation[0], self.hsv_threshold_value[0]), (
                self.hsv_threshold_hue[1], self.hsv_threshold_saturation[1], self.hsv_threshold_value[1])
        )

        kernel = np.ones((6, 6), np.uint8)
        image_erode = cv2.erode(mask, kernel, iterations=1)
        image_dilate = cv2.dilate(image_erode, kernel, iterations=1)

        return image_dilate

    def find_contours(self, input):
        contours, hierarchy = cv2.findContours(
            input, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def filter_contours(
        self,
        source,
        input_contours
    ):
        output = []
        center = []
        for contour in input_contours:

            x, y, w, h = cv2.boundingRect(contour)
            if w < self.filter_contours_min_width or w > self.filter_contours_max_width:
                continue
            if h < self.filter_contours_min_height or h > self.filter_contours_max_height:
                continue
            area = cv2.contourArea(contour)
            if area < self.filter_contours_min_area:
                continue
            if cv2.arcLength(contour, True) < self.filter_contours_min_perimeter:
                continue
            hull = cv2.convexHull(contour)
            solid = 100 * area / cv2.contourArea(hull)
            if solid < self.filter_contours_solidity[0] or solid > self.filter_contours_solidity[1]:
                continue
            if len(contour) < self.filter_contours_min_vertices or len(contour) > self.filter_contours_max_vertices:
                continue
            ratio = (float)(w) / h
            if ratio < self.filter_contours_min_ratio or ratio > self.filter_contours_max_ratio:
                continue
            output.append(contour)

            M = cv2.moments(contour)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.circle(source, (cX, cY), 3, (255, 0, 255), -1)
            cv2.circle(source, (cX, cY), 10, (255, 0, 255), 2)
            x = cX
            y = cY
            center.append([x, y])
        return center


class red(ball):
    def __init__(self):
        super().__init__()
        self.__hsv_threshold_hue1 = [0, 20]
        self.__hsv_threshold_hue2 = [146, 180]
        self.__hsv_threshold_saturation = [30, 255]
        self.__hsv_threshold_value = [40, 255]

    def process(self, source):
        self.rgb_threshold_input = source
        self.hsv_threshold_output = self.__hsv_threshold(
            self.rgb_threshold_input,
            self.__hsv_threshold_hue1,
            self.__hsv_threshold_hue2,
            self.__hsv_threshold_saturation,
            self.__hsv_threshold_value,
        )

        self.find_contours_output = self.find_contours(
            self.hsv_threshold_output)

        return self.hsv_threshold_output, self.filter_contours(
            source,
            self.find_contours_output,
        )

    @staticmethod
    def __hsv_threshold(input, hue1, hue2, saturation, value):
        out = cv2.cvtColor(input, cv2.COLOR_BGR2HSV)

        mask1 = cv2.inRange(
            out, (hue1[0], saturation[0], value[0]
                  ), (hue1[1], saturation[1], value[1])
        )
        mask2 = cv2.inRange(
            out, (hue2[0], saturation[0], value[0]
                  ), (hue2[1], saturation[1], value[1])
        )
        mask = cv2.bitwise_or(mask1, mask2)

        kernel = np.ones((5, 5), np.uint8)
        image_erode = cv2.erode(mask, kernel, iterations=1)
        image_dilate = cv2.dilate(image_erode, kernel, iterations=1)

        return image_dilate

class yellow(ball):
    def __init__(self):
        super().__init__()
        self.hsv_threshold_hue = [10, 25]
        self.hsv_threshold_saturation = [50, 255]
        self.hsv_threshold_value = [56, 255]

    def process(self, source):
        return super().process(source)

class white(ball):
    def __init__(self):
        super().__init__()
        self.hsv_threshold_hue = [0, 180]
        self.hsv_threshold_saturation = [0, 40]
        self.hsv_threshold_value = [0, 255]

    def process(self, source):
        return super().process(source)

class blue(ball):
    def __init__(self):
        super().__init__()
        self.hsv_threshold_hue = [0, 180]
        self.hsv_threshold_saturation = [0, 40]
        self.hsv_threshold_value = [0, 255]

    def process(self, source):
        return super().process(source)

class green(ball):
    def __init__(self):
        super().__init__()
        self.hsv_threshold_hue = [25, 87]
        self.hsv_threshold_saturation = [43, 255]
        self.hsv_threshold_value = [0, 255]

    def process(self, source):
        return super().process(source)

class black(ball):
    def __init__(self):
        super().__init__()
        self.hsv_threshold_hue = [0, 180]
        self.hsv_threshold_saturation = [0, 40]
        self.hsv_threshold_value = [0, 255]

    def process(self, source):
        return super().process(source)
