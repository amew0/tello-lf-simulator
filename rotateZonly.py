import numpy as np
from djitellopy import tello
import cv2
from time import sleep
from QRcodeFunc import *

def rotateZ(cx, cy):
    height_half = height//2
    width_half = width//2
    if cy != height_half:
        slope = (cx - width_half) / (cy - height_half)
        theta = round((np.arctan(slope)) * (180 / np.pi))

        speed = 50
        degree2turns = 75 / 360
        pyv = 0
        nyv = 0
        # yv = theta*degree2turns()
        if cx == width_half or cy == height_half:
            return None
        elif cx < width_half:
            nyv = -round(theta*degree2turns*speed)
        elif cx > width_half:
            pyv = round(theta*degree2turns*speed)
        print(pyv,nyv)
        while pyv > 0:
            me.send_rc_control(0, 0, 0, 99)
            pyv -= 99
        while nyv < 0:
            me.send_rc_control(0, 0, 0, -99)
            nyv += 99
    return False

def rotateZ_(cx,cy):
    height_half = height//2
    width_half = width//2
    if cy != height_half:
        slope = (cx - width_half) / (cy - height_half)
        theta = round((np.arctan(slope)) * (180 / np.pi))
        if cx < width_half and cy < height_half:
            me.rotate_counter_clockwise(theta)
        elif cx < width_half and cy > height_half:
            me.rotate_counter_clockwise(180+theta)
        elif cx > width_half and cy > height_half:
            me.rotate_clockwise(180-theta)
        elif cx > width_half and cy < height_half:
            me.rotate_clockwise(-1*theta)
    return False

def main():
    init()
    global me,curve, height, width, img

    me = tello.Tello()
    me.connect()
    me.streamon()
    sleep(5)
    width, height = 480, 360
    cx, cy = 240, 0
    notdone = True
    while notdone:
        vals = getKeyboardInput(me, False)
        me.send_rc_control(vals[0], vals[1], vals[2], vals[3])  # LR, BF, DU, YV
        # _, img = cap.read()
        img = me.get_frame_read().frame
        img = cv2.resize(img, (width, height))
        img = cv2.flip(img, 0)

        img = cv2.putText(img, str(me.get_battery()), (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        img = cv2.circle(img, (cx, cy), 10, (0, 255, 125), cv2.FILLED)
        
        if vals[4]:
            notdone = rotateZ_(cx, cy)
            
        cv2.imshow("Output", img)

        cv2.waitKey(1)

        
if __name__ == "__main__":
    main()