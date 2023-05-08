import cv2
from djitellopy import tello
from time import sleep

# Local imports
from QRcodeFunc import *

# cap = cv2.VideoCapture(0)

init()
me = tello.Tello()
me.connect()

# starting the video stream
me.streamoff()
sleep(0.5)
me.takeoff()

me.streamon()

i = 0
while True:
    img = me.get_frame_read().frame
    img = cv2.flip(img, 0)

    r = False
    vals = getKeyboardInput(me, r)
    me.send_rc_control(vals[0], vals[1], vals[2], vals[3])  # LR, BF, DU, YV
    sleep(0.05)
    # found = decoder(me, img, i)
    # if i % 40 == 0:
        # if not found: 
            # me.move_forward(20)

        # img = cv2.putText(img, str(me.get_battery()), (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    cv2.imshow('Image', img)

    if cv2.waitKey(10) == 'q':
        break
    
    i += 1

# import numpy as np
# height = 360
# width = 480
# def rotateZ(cx, cy):
#     height_half = height/2
#     width_half = width/2
#     slope = (cx - width/2) / (cy - height/2)
#     theta = (np.arctan(slope)) * (180 / np.pi)

#     if cx < width_half and cy < height_half:
#         print(f"me.rotate_counter_clockwise({theta})")
#     elif cx < width_half and cy > height_half:
#         print(f"me.rotate_counter_clockwise(180+{theta})")
#     elif cx > width_half and cy > height_half:
#         print(f"me.rotate_clockwise(180-{theta})")
#     elif cx > width_half and cy < height_half:
#         print(f"me.rotate_clockwise(-1*{theta})")
#     else:
#         return None
    
# rotateZ(455, 100)