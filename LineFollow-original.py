import numpy as np
from djitellopy import tello
import cv2
from time import sleep
from QRcodeFunc import *

me = tello.Tello()

me.connect()

print(me.get_battery())

me.streamon()
sleep(5)

# me.move_down(20)


cap = cv2.VideoCapture(1)

hsvVals = [0,0,212,179,255,255]

sensors = 3

threshold = 0.2

width, height = 480, 360

senstivity = 3  # if number is high less sensitive

weights = [-25, -15, 0, 15, 25]

fSpeed = 20

curve = 0

def thresholding(img):

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower = np.array([hsvVals[0], hsvVals[1], hsvVals[2]])

    upper = np.array([hsvVals[3], hsvVals[4], hsvVals[5]])

    mask = cv2.inRange(hsv, lower, upper)

    return mask

def getContours(imgThres, img):

    cx = 0
    X=0

    contours, hieracrhy = cv2.findContours(imgThres, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if len(contours) != 0:

        biggest = max(contours, key=cv2.contourArea)

        x, y, w, h = cv2.boundingRect(biggest)

        cx = x + w // 2

        cy = y + h // 2

        cv2.drawContours(img, biggest, -1, (255, 0, 255), 7)

        cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

        # X= int(np.average(biggest[:,0,0]))
        # Y=int(np.average(biggest[:,0,1]))
        # cv2.drawContours(img, biggest, -1, (255, 0, 255), 7)
        # cv2.circle(img, (X, Y), 10, (0, 0, 255), cv2.FILLED)

    return cx
    # return X

def getSensorOutput(imgThres, sensors):

    imgs = np.hsplit(imgThres, sensors)

    totalPixels = (img.shape[1] // sensors) * img.shape[0]

    senOut = []

    for x, im in enumerate(imgs):

        pixelCount = cv2.countNonZero(im)

        if pixelCount > threshold * totalPixels:

            senOut.append(1)

        else:

            senOut.append(0)

        # cv2.imshow(str(x), im)

    # print(senOut)

    return senOut

def sendCommands(senOut, cx):

    global curve

    ## TRANSLATION

    lr = (cx - width // 2) // senstivity

    lr = int(np.clip(lr, -10, 10))

    if 2 > lr > -2: lr = 0

    ## Rotation

    if   senOut == [1, 0, 0]: curve = weights[0]

    elif senOut == [1, 1, 0]: curve = weights[1]

    elif senOut == [0, 1, 0]: 
        curve = weights[2]
        me.send_rc_control(lr, fSpeed, 0, curve)


    elif senOut == [0, 1, 1]: curve = weights[3]

    elif senOut == [0, 0, 1]: curve = weights[4]

    elif senOut == [0, 0, 0]: curve = weights[2]

    elif senOut == [1, 1, 1]: curve = weights[2]

    elif senOut == [1, 0, 1]: curve = weights[2]

    me.send_rc_control(lr, 15, 0, curve)

qr_found = None
init()
first = True
counter = 0
while True:

    #_, img = cap.read()
    # vals = getKeyboardInput(me, False)

    # me.send_rc_control(vals[0], vals[1], vals[2], vals[3])  # LR, BF, DU, YV
    

    img = me.get_frame_read().frame

    img = cv2.resize(img, (width, height))

    img = cv2.flip(img, 0)

    imgThres = thresholding(img)

    cx = getContours(imgThres, img)  ## For Translation

    senOut = getSensorOutput(imgThres, sensors)  ## Rotation

    if first:
        me.takeoff()
        first = False

    sendCommands(senOut, cx)

    val = decoder(me, img, qr_found, fw=30)
    if val !=  None:
        qr_found = val

        if qr_found == "CLOCK":
            counter += 1

        if counter == 2:
            me.move_forward(50)

    cv2.imshow("Output", img)

    cv2.imshow("Path", imgThres)

    cv2.waitKey(1)