import pygame
import cv2
import numpy as np
from time import sleep

pygame.init()

GREEN = (0,255,0)
RED = (255,0,0)
BLUE = (0,0,255)

# set the dimensions of the window
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600

WINDOW_WIDTH_CENTER = WINDOW_WIDTH // 2
WINDOW_HEIGHT_CENTER = WINDOW_HEIGHT // 2
BOX_WIDTH = 240
BOX_HEIGHT = 180
DRONE_INIT_X = WINDOW_WIDTH_CENTER # center_x of the box
DRONE_INIT_Y = int(WINDOW_HEIGHT - BOX_HEIGHT/2) # center_y of the box
BOX_X = int(DRONE_INIT_X - BOX_WIDTH/2) # leftupper_x of the box
BOX_Y = int(DRONE_INIT_Y - BOX_HEIGHT/2) # leftupper_y of the box

space = pygame.image.load("path_1.png")
# white = pygame.image.load("white.png")
black = pygame.image.load("black_900x600.png")
global screen
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Simulator")

def render_box():
    rot = theta % 360
    b_z_size = ((1+b_z)*WINDOW_WIDTH, (1+b_z)*WINDOW_HEIGHT)

    # create a new surface with an empty transparent region
    box_offset = 0 # to make the box a little bigger than the drone. It should be greater than the thickness
    global surf
    surf = pygame.Surface((BOX_WIDTH+box_offset, BOX_HEIGHT+box_offset), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    box_thickness = 3
    pygame.draw.rect(surf, GREEN, surf.get_rect(), box_thickness)

    # Create a surface to hold the space.png
    surf_space = pygame.Surface((WINDOW_WIDTH,WINDOW_HEIGHT), pygame.SRCALPHA)
    surf_space.blit(space , (0,0) )  
    
    rect = surf_space.get_rect(center=(b_x,b_y)) 
    old_center = rect.center  
    surf_space = pygame.transform.scale(surf_space, b_z_size) 

    surf_space = pygame.transform.rotate(surf_space , rot) 
    
    
    rect = surf_space.get_rect()  
    rect.center = old_center  

    screen.blit(surf_space , rect)
    # pygame.display.flip()  

def get_frame_read():
    # convert the surface to a numpy array
    array = pygame.surfarray.array3d(screen)
    image = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)

    # get the image under the Rectangle (Box)
    image_under = image[BOX_X :BOX_X+BOX_WIDTH,BOX_Y:BOX_Y+BOX_HEIGHT:]
    image_under = cv2.flip(cv2.rotate(image_under, cv2.ROTATE_90_CLOCKWISE), 1)
    
    screen.blit(surf , surf.get_rect(center=(DRONE_INIT_X,DRONE_INIT_Y)))   
    pygame.display.flip()
    return image_under

def getKey(keyName):
    ans = False
    for eve in pygame.event.get(): pass
    keyInput = pygame.key.get_pressed()
    mykey = getattr(pygame, 'K_{}'.format(keyName))
    if keyInput[mykey]:
        ans = True
    pygame.display.update()
    return ans
def getKeyboardInput_(r):
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 1

    if getKey("LEFT"): lr = -speed
    elif getKey("RIGHT"): lr = speed
    elif getKey("UP"): fb = speed         #FWD
    elif getKey("DOWN"): fb = -speed    #BACK
    elif getKey("w"): ud = speed          #up
    elif getKey("s"): ud = -speed       #DOWN
    elif getKey("a"): yv = -speed         #AntiCLK
    elif getKey("d"): yv = speed        #CLK
    elif getKey("e"): print("land")
    
    elif getKey("q") and not r: 
        print("takeoff")
        sleep(0.5)
        print("move up")
        sleep(0.05)
        r = not r

    elif getKey("f"): print("flip")
    if getKey("r"): 
        r = True
        print("Battery level")
    return [lr, fb, ud, yv, r]

def send_rc_control(a:int, b:int, c:int, d:int):
    a *= -1
    c *= -1
    global b_x,b_y,b_z,theta

    print(f"Sending {a} - {b} - {c} - {d}")
    b_x += a*sensitivity
    b_y += b*sensitivity
    b_z += c*0.01*sensitivity
    theta += d
    # return image
    if b_z <= -0.99: b_z = -0.99

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
    lr = (cx - width // 2) // sensitivity
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
    send_rc_control(lr, fSpeed, 0, curve)

def get_battery():
    return 100
# Clock
clock = pygame.time.Clock()

global surf, weight, threshold, sensitivity, hsvVals, height, width, img, sensors, curve, b_x, b_y, b_z, theta, fSpeed
fSpeed = 1
weights = [i for i in range(-2, 3)] # make sure 5 values are generated
threshold = 0.20
sensitivity = 2
hsvVals =  [0,0,193,179,255,255]
sensors = 3
threshold = 0.20
width, height = 240, 180
curve = 0

running = True
b_x,b_y,b_z,theta= WINDOW_WIDTH_CENTER,WINDOW_HEIGHT_CENTER,0,0
tookoff = False

while running:
    # handle Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    vals = getKeyboardInput_(tookoff)

    # clear the screen
    screen.fill((255, 255, 255))
    screen.blit(black, (0, 0))

    # and read the frame read after the sent command
    send_rc_control(vals[0], vals[1], vals[2], vals[3])
    render_box()
    img = get_frame_read()
    tookoff = vals[4]
    if tookoff:
        # img = cv2.imread("path.png")
        img = cv2.resize(img, (width, height))
        imgThres = thresholding(img, hsvVals)
        cx,cy = getContours(imgThres, img)
        senOut = getSensorOutput(imgThres, sensors)
        cv2.imshow("Path", imgThres)
        img = cv2.putText(img, str(get_battery()), (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        cv2.imshow("Output", img)

        sendCommands(senOut, cx, cy)
        cv2.waitKey(1)
    
    # Part of event loop
    clock.tick(30)

# quit Pygame
pygame.quit()
cv2.waitKey(0)
cv2.destroyAllWindows()