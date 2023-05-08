import numpy as np
from djitellopy import tello
import cv2
from time import sleep
from QRcodeFunc import *

def thresholding(img, hsvVals):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([hsvVals[0], hsvVals[1], hsvVals[2]])
    upper = np.array([hsvVals[3], hsvVals[4], hsvVals[5]])
    mask = cv2.inRange(hsv, lower, upper)
    return mask

def getContours(imgThres, img):
    cx, cy = 0,0
    # X = 0
    # Y = 0
    contours, hieracrhy = cv2.findContours(imgThres, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if len(contours) != 0:
        biggest = max(contours, key=cv2.contourArea)
        X= int(np.average(biggest[:,0,0]))
        Y=int(np.average(biggest[:,0,1]))
        cv2.drawContours(img, biggest, -1, (255, 0, 255), 7)
        cv2.circle(img, (X, Y), 10, (0, 0, 255), cv2.FILLED)
        # x, y, w, h = cv2.boundingRect(biggest)
        # cx = x + w // 2
        # cy = y + h // 2
        # cv2.drawContours(img, biggest, -1, (255, 0, 255), 7)
        # cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
    return cx, cy
    # return X, Y

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
        cv2.imshow(str(x), im)
    # print(senOut)
    return senOut

def sendCommands(senOut, cx, cy):
    # rotateZ(cx, cy)

    global curve
    ## TRANSLATION
    lr = (cx - width // 2) // senstivity
    lr = int(np.clip(lr, -10, 10))
    if 2 > lr > -2: lr = 0
    ## Rotation
    if   senOut == [1, 0, 0]: curve = weights[0]
    elif senOut == [1, 1, 0]: curve = weights[1]
    elif senOut == [0, 1, 0]: curve = weights[2]
    elif senOut == [0, 1, 1]: curve = weights[3]
    elif senOut == [0, 0, 1]: curve = weights[4]
    elif senOut == [0, 0, 0]: curve = weights[2]
    elif senOut == [1, 1, 1]: 
        curve = weights[2] # just like 1 0 0 but without fSpeed
        # me.send_rc_control(0, 0, 0, curve)
        # return 1

    elif senOut == [1, 0, 1]: curve = weights[2]
    me.send_rc_control(lr, fSpeed, 0, curve)

    # print("command sent")
    return 1

def rotateZ(cx,cy):
    height_half = height//2
    width_half = width//2
    if cy != height_half:
        slope = (cx - width_half) / (cy - height_half)
        theta = round((np.arctan(slope)) * (180 / np.pi))
        theta //= senstivity
        if cx < width_half and cy < height_half:
            me.rotate_counter_clockwise(theta)
        elif cx < width_half and cy > height_half:
            me.rotate_counter_clockwise(180+theta)
        elif cx > width_half and cy > height_half:
            me.rotate_clockwise(180-theta)
        elif cx > width_half and cy < height_half:
            me.rotate_clockwise(-1*theta)


def main():
    init()
    global me, cap, senstivity, fSpeed, curve, weights, hsvVals, height, width, threshold, img

    me = tello.Tello()
    me.connect()
    print(me.get_battery())
    me.streamon()
    # me.takeoff()
    # me.move_down(20)
    sleep(5)

    cap = cv2.VideoCapture(1)
    hsvVals =  [0,0,193,179,255,255]
    sensors = 3
    threshold = 0.20
    width, height = 480, 360
    senstivity = 3  # if number is high less sensitive
    weights = [-25, -15, 0, 15, 25]
    weights = [int(i*1) for i in weights]
    fSpeed = 15
    curve = 0
    qr_found = None
    i = 0
    while True:
        vals = getKeyboardInput(me, False)
        me.send_rc_control(vals[0], vals[1], vals[2], vals[3])  # LR, BF, DU, YV
        # _, img = cap.read()
        img = me.get_frame_read().frame
        img = cv2.resize(img, (width, height))
        img = cv2.flip(img, 0)
        
        # val = decoder(me, img, qr_found, fw=30)
        # if val !=  None:
        #     qr_found = val
        imgThres = thresholding(img, hsvVals)
        cx,cy = getContours(imgThres, img)  ## For Translation
        senOut = getSensorOutput(imgThres, sensors)  ## Rotation
        cv2.imshow("Path", imgThres)
        img = cv2.putText(img, str(me.get_battery()), (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        cv2.imshow("Output", img)
        # if vals[4]:
            # print("command will be sent")
        sendCommands(senOut, cx, cy)
        cv2.waitKey(1)

        
if __name__ == "__main__":
    main()