import cv2
import numpy as np  

img = cv2.imread("path.png")
hsvVals =  [0,0,193,179,255,255]


def thresholding(img, hsvVals):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([hsvVals[0], hsvVals[1], hsvVals[2]])
    upper = np.array([hsvVals[3], hsvVals[4], hsvVals[5]])
    mask = cv2.inRange(hsv, lower, upper)
    return mask

def getContours(imgThres, img):
    cx, cy = 0,0
    contours, _ = cv2.findContours(imgThres, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if len(contours) != 0:
        biggest = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(biggest)
        cx = x + w // 2
        cy = y + h // 2
        cv2.drawContours(img, biggest, -1, (255, 0, 255), 7)
        cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
    return cx, cy

while True:
    img = cv2.imread("path.png")

    imgThres = thresholding(img, hsvVals)
    cv2.imshow("0", imgThres)
    cx,cy = getContours(imgThres, img)  ## For Translation
    cv2.imshow("Output", img)


    

    if (cv2.waitKey(1) & 0xFF == ord('q')):
        break
cv2.destroyAllWindows()