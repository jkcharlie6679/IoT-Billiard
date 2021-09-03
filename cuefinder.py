import cv2
import numpy as np

class CueFinder:

    def __init__(self):

        self.__hsv_threshold_hue = [0, 180]
        self.__hsv_threshold_saturation = [0, 43]
        self.__hsv_threshold_value = [46, 255]

        
        self.cue_length_max = 3600
        self.minLineLength = 60 # parameter for HoughLinesP

    def process(self, source0):

        self.__rgb_threshold_input = source0
        self.hsv_threshold_output = self.__hsv_threshold(
            self.__rgb_threshold_input,
            self.__hsv_threshold_hue,
            self.__hsv_threshold_saturation,
            self.__hsv_threshold_value,
        )

        return self.hsv_threshold_output, self.__find_cue(source0, self.hsv_threshold_output)

    @staticmethod
    def __hsv_threshold(input, hue, saturation, value):
        out = cv2.cvtColor(input, cv2.COLOR_BGR2HSV)
        
        mask =  cv2.inRange(
            out, (hue[0], saturation[0], value[0]), (hue[1], saturation[1], value[1])
        )
        kernel = np.ones((5, 5), np.uint8)
        image_dilate = cv2.dilate(mask, kernel, iterations=1)
        return image_dilate

    def __find_cue(self, frame, input):
        lines = cv2.HoughLinesP(input, 1, np.pi / 180, 100, minLineLength=self.minLineLength, maxLineGap=1)
        get_cue = []
        if type(lines) is np.ndarray:
            for x1, y1, x2, y2 in lines[0]:
                l = (x1 - x2)**2 + (y1 - y2)**2
                if l < self.cue_length_max:
                    continue
                cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 0), 2)
                get_cue.append([x1, y1])
                get_cue.append([x2, y2])

        return get_cue
