from telloSimulator import TelloSimulator
from time import sleep
import pygame
import cv2
from QRcodeFunc import *

global me
me = TelloSimulator()

me.connect(path_image_loc="path_3.png")
me.get_battery()
me.streamon()
me.sensitivity = 2

clock = pygame.time.Clock()

# global surf, weight, threshold, sensitivity, hsvVals, height, width, img, sensors, curve, b_x, b_y, b_z, theta, fSpeed
fSpeed = 1
weights = [i for i in range(-2, 3)] # make sure 5 values are generated
threshold = 0.20
sensitivity = 2
hsvVals =  [0,0,193,179,255,255]
sensors = 3
threshold = 0.20
curve = 0

running = True
'''
def getKey(keyName):
    ans = False
    for eve in pygame.event.get(): pass
    keyInput = pygame.key.get_pressed()
    mykey = getattr(pygame, 'K_{}'.format(keyName))
    if keyInput[mykey]:
        ans = True
    pygame.display.update()
    return ans
'''

def getKeyboardInput():
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 1
    global me
    if getKey("LEFT"): lr = -speed
    elif getKey("RIGHT"): lr = speed
    elif getKey("UP"): fb = speed         #FWD
    elif getKey("DOWN"): fb = -speed    #BACK
    elif getKey("w"): ud = speed          #up
    elif getKey("s"): ud = -speed       #DOWN
    elif getKey("a"): yv = -speed         #AntiCLK
    elif getKey("d"): yv = speed        #CLK
    elif getKey("l"): me.land()
    elif getKey("t"): me.take_off()
    elif getKey("f"): print("flip")
    return [lr, fb, ud, yv]


def thresholding(img, hsvVals):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([hsvVals[0], hsvVals[1], hsvVals[2]])
    upper = np.array([hsvVals[3], hsvVals[4], hsvVals[5]])
    mask = cv2.inRange(hsv, lower, upper)
    return mask

def getContours(imgThres, img):
    cx, cy = 0,0
    X = 0
    Y = 0
    contours, hieracrhy = cv2.findContours(imgThres, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if len(contours) != 0:
        biggest = max(contours, key=cv2.contourArea)
        X= int(np.average(biggest[:,0,0]))
        Y=int(np.average(biggest[:,0,1]))
        cv2.drawContours(img, biggest, -1, (255, 0, 255), 7)
        cv2.circle(img, (X, Y), 10, (0, 0, 255), cv2.FILLED)

        x, y, w, h = cv2.boundingRect(biggest)
        cx = x + w // 2
        cy = y + h // 2
        cv2.drawContours(img, biggest, -1, (255, 0, 255), 7)
        cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
    return X, Y
    # return cx, cy

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

def sendCommands(senOut, cx, cy):
    ## TRANSLATION
    lr = (cx - me.BOX_WIDTH // 2) // sensitivity
    lr = int(np.clip(lr, -10, 10))
    if 2 > lr > -2: lr = 0
    ## Rotation
    global curve
    if   senOut == [1, 0, 0]: curve = weights[0]
    elif senOut == [1, 1, 0]: curve = weights[1]
    elif senOut == [0, 1, 0]: curve = weights[2]
    elif senOut == [0, 1, 1]: curve = weights[3]
    elif senOut == [0, 0, 1]: curve = weights[4]
    elif senOut == [0, 0, 0]: curve = weights[2]
    elif senOut == [1, 1, 1]: curve = weights[2]
    elif senOut == [1, 0, 1]: curve = weights[2]
    me.send_rc_control(lr, fSpeed, 0, curve)

while running:
    # handle Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    vals = getKeyboardInput()

    # # and read the frame read after the sent command
    me.send_rc_control(vals[0], vals[1], vals[2], vals[3])

    img = me.get_frame_read()
    # img = cv2.imread("path.png")
    img = cv2.resize(img, (me.BOX_WIDTH, me.BOX_HEIGHT))
    imgThres = thresholding(img, hsvVals)
    cx,cy = getContours(imgThres, img)
    senOut = getSensorOutput(imgThres, sensors)
    cv2.imshow("Path", imgThres)
    img = cv2.putText(img, str(me.get_battery()), (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    cv2.imshow("Output", img)

    if me.tookoff:
        sendCommands(senOut, cx, cy)
    cv2.waitKey(1)
    
    # Part of event loop
    clock.tick(30)

# quit Pygame
pygame.quit()
cv2.waitKey(0)
cv2.destroyAllWindows()

