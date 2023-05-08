import cv2
import numpy as np
from pyzbar.pyzbar import decode
from djitellopy import tello
# import time
import pygame
from time import sleep
  

def decoder(me, image, qr_found, i=0, fw=40, save_decoded=False):
    gray_img = cv2.cvtColor(image, 0)
    barcode = decode(gray_img)
    barcodeData = None
    for obj in barcode:
        barcodeData = obj.data.decode("utf-8")
        barcodeType = obj.type
        string = "Data " + str(barcodeData) + " | Type " + str(barcodeType)

        if barcodeData == qr_found:
            return None
        points = obj.polygon
        (x, y, w, h) = obj.rect
        pts = np.array(points, np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(image, [pts], True, (0, 255, 0), 3)

        
        if save_decoded:

            cv2.putText(image, string, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            cv2.imwrite(f"{barcodeData}_{i}.png", image)
        print("Barcode: " + barcodeData + " | Type: " + barcodeType)
        if barcodeData == "UP":
            me.move_up(50)
            # sleep(0.5)
            # me.move_down(50)
            # me.move_forward(30)

        
        # elif barcodeData == "FLIP":
        #     me.flip_forward()
                
        elif barcodeData == "CLOCK":
            me.rotate_clockwise(360)
        
        elif barcodeData == "LAND":
            me.land()
        
        # me.move_forward(fw)
    
    # return len(barcode) != 0
    return barcodeData

def init():
    pygame.init()
    win = pygame.display.set_mode((360,240))

def getKey(keyName):
    ans = False
    for eve in pygame.event.get(): pass
    keyInput = pygame.key.get_pressed()
    mykey = getattr(pygame, 'K_{}'.format(keyName))
    if keyInput[mykey]:
        ans = True
    pygame.display.update()
    return ans
def getKeyboardInput(me, r):
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
    elif getKey("e"): me.land()
    elif getKey("q"): 
        me.takeoff()
        me.move_down(20)
        r = True

    elif getKey("f"): me.flip_forward()
    if getKey("r"): 
        r = True
        print(me.get_battery())

    

    # if getKey("p"): cv2.imwrite(f"{i}.png", frame_read.frame)

    return [lr, fb, ud, yv, r]
    
