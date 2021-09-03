import cv2
import os

projFolder = os.path.abspath('.')
pos_folder = os.path.join(projFolder, "dataset/pos/")
neg_folder = os.path.join(projFolder, "dataset/neg/")
positiveDesc_file = os.path.join(projFolder, "dataset/pos.info")
negativeDesc_file = os.path.join(projFolder, "dataset/neg.info")

with open(positiveDesc_file, 'a') as the_file:
    for file in os.listdir(pos_folder):
        filename, file_extension = os.path.splitext(file)
        if(file_extension.lower()==".jpg" or file_extension.lower()==".png" or file_extension.lower()==".jpeg"):
            img = cv2.imread(os.path.join(pos_folder ,file))
            sizeimg = img.shape
            the_file.write("pos/" + file + '  1  0 0 ' + str(sizeimg[1]) + ' ' + str(sizeimg[0]) + '\n')

with open(negativeDesc_file, 'a') as the_file:
    for file in os.listdir(neg_folder):
        filename, file_extension = os.path.splitext(file)
        if(file_extension.lower()==".jpg" or file_extension.lower()==".png" or file_extension.lower()==".jpeg"):
            the_file.write("neg/" + file + '\n')
