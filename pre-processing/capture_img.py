import cv2
import os

cap = cv2.VideoCapture(0)

image_path = "./img"
os.chdir(image_path)


while cap.isOpened():
    ret, frame = cap.read()
    cv2.imwrite("1.jpg", frame)
    i = 0
    if ret:
        i += 1
        cv2.imwrite(str(i)+".jpg", frame)
        cv2.imshow("video", frame)
        if cv2.waitKey(1) == ord("q"):
            break


cap.release()
cv2.destroyAllWindows()

