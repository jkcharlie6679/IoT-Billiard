import cv2
import json
import os
import configparser

cfgpath = os.path.abspath(".") + "/config.ini"

config = configparser.ConfigParser()
config.read(cfgpath)

json_folder = "./dataset/img_json/"
img_folder = "./dataset/img/"
pos_folder = "./dataset/pos/"
neg_folder = "./dataset/neg/"

for file in os.listdir(json_folder):
    filename, file_extension = file.split(".")
    if file_extension == "json":
        img = cv2.imread(img_folder + filename + ".jpg")
        with open(json_folder + file) as json_file:
            data = json.loads(json_file.read())
            index = -1
            # get label
            for label in data["shapes"]:
                x2, y2 = 0, 0
                x1 = img.shape[0]
                y1 = img.shape[1]
                index += 1
                # resize the label
                for point in label["points"]:
                    if x1 > point[0]:
                        x1 = point[0]
                    if x2 < point[0]:
                        x2 = point[0]
                    if y1 > point[1]:
                        y1 = point[1]
                    if y2 < point[1]:
                        y2 = point[1]
                crop_img = img[int(y1) : int(y2), int(x1) : int(x2)]
                cv2.imwrite(
                    pos_folder + filename + "_" + str(index) + ".jpg", crop_img
                )
                img[int(y1) : int(y2), int(x1) : int(x2)] = 0
        # generate negative image
        for j in range(0, img.shape[1] - 100, 100):
            for k in range(0, img.shape[0] - 100, 100):
                neg_img = img[k : k + 100, j : j + 100]
                cv2.imwrite(
                    neg_folder
                    + filename
                    + "_"
                    + str(int(j / 100))
                    + str(int(k / 100))
                    + ".jpg",
                    neg_img,
                )
