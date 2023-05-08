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
    cx = 0
    X = 0
    Y = 0
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
    # return cx
    return X, Y

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
    rotateZ(cx, cy)

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
    elif senOut == [1, 1, 1]: curve = weights[2]
    elif senOut == [1, 0, 1]: curve = weights[2]
    send_rc_control(lr, fSpeed, 0, curve)
    print("command sent")

def rotateZ(cx,cy):
    height_half = height//2
    width_half = width//2
    if cy != height_half:
        slope = (cx - width_half) / (cy - height_half)
        theta = round((np.arctan(slope)) * (180 / np.pi))
        theta //= senstivity
        if cx < width_half and cy < height_half:
            print(f"RCC - {theta}")
        elif cx < width_half and cy > height_half:
            print(f"RCC - {180+theta}")
        elif cx > width_half and cy > height_half:
            print(f"RC - {180-theta}")
        elif cx > width_half and cy < height_half:
            print(f"RC - {-1*theta}")

def getKeyboardInput_(r):
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 50

    if getKey("LEFT"): lr = -speed
    elif getKey("RIGHT"): lr = speed
    elif getKey("UP"): fb = speed         #FWD
    elif getKey("DOWN"): fb = -speed    #BACK
    elif getKey("w"): ud = speed          #up
    elif getKey("s"): ud = -speed       #DOWN
    elif getKey("a"): yv = -speed         #AntiCLK
    elif getKey("d"): yv = speed        #CLK
    elif getKey("e"): print("land")
    elif getKey("q"): 
        print("takeoff")
        sleep(0.5)
        print("move up")
        sleep(0.05)
        r = True

    elif getKey("f"): print("flip")
    if getKey("r"): 
        r = True
        print("Battery level")
    return [lr, fb, ud, yv, r]

def send_rc_control(a,b,c,d):
    print(f"Sending {a} - {b} - {c} - {d}")

def main():
    init()
    global me, cap, senstivity, fSpeed, curve, weights, hsvVals, height, width, threshold, img

    cap = cv2.VideoCapture(1)
    hsvVals =  [0,0,193,179,255,255]
    sensors = 3
    threshold = 0.20
    width, height = 480, 360
    senstivity = 3  # if number is high less sensitive
    weights = [-25, -15, 0, 15, 25]
    fSpeed = 30
    curve = 0

    while True:
        vals = getKeyboardInput_(False)
        send_rc_control(vals[0], vals[1], vals[2], vals[3])
        _, img = cap.read()
        img = cv2.resize(img, (width, height))

        imgThres = thresholding(img, hsvVals)
        cx,cy = getContours(imgThres, img)  ## For Translation
        senOut = getSensorOutput(imgThres, sensors)  ## Rotation
        cv2.imshow("Path", imgThres)
        img = cv2.putText(img, "100%", (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        cv2.imshow("Output", img)
        if vals[4]:
            print("command will be sent")
        sendCommands(senOut, cx, cy)
        cv2.waitKey(1)

        
if __name__ == "__main__":
    main()