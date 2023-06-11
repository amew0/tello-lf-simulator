import pygame
import cv2
import numpy as np
from time import sleep

class TelloSimulator:
    def __init__ (self):
        self.tookoff = False
        self.battery_level = 100
        self.sensitivity = 1

        self.WINDOW_WIDTH = 900
        self.WINDOW_HEIGHT = 600
        self.WINDOW_WIDTH_CENTER = self.WINDOW_WIDTH // 2
        self.WINDOW_HEIGHT_CENTER = self.WINDOW_HEIGHT // 2
        self.BOX_WIDTH = 240
        self.BOX_HEIGHT = 180
        self.DRONE_INIT_X = self.WINDOW_WIDTH_CENTER # center_x of the box
        self.DRONE_INIT_Y = int(self.WINDOW_HEIGHT - self.BOX_HEIGHT/2) # center_y of the box
        self.BOX_X = int(self.DRONE_INIT_X - self.BOX_WIDTH/2) # leftupper_x of the box
        self.BOX_Y = int(self.DRONE_INIT_Y - self.BOX_HEIGHT/2) # leftupper_y of the box
        
        self.GREEN = (0,255,0)
        self.RED = (255,0,0)
        self.BLUE = (0,0,255)

        self.lr = self.WINDOW_WIDTH_CENTER
        self.fb = self.WINDOW_HEIGHT_CENTER
        self.ud = 0
        self.yv = 0

        self.box_offset = 6

        self.path_image_loc = None
        self.screen = None
        self.background = None
        self.path_image = None
        self.box = None
        
        print("Tello Simulator Initialized")

    def get_battery(self):
        return self.battery_level

    def connect(self, background_loc="black_900x600.png", path_image_loc="path_1.png"):
        
        self.screen = pygame.display.set_mode([self.WINDOW_WIDTH, self.WINDOW_HEIGHT])
        self.background = pygame.image.load(background_loc)
        self.path_image = pygame.image.load(path_image_loc)
        self.box = pygame.Surface((self.BOX_WIDTH+self.box_offset, self.BOX_HEIGHT+self.box_offset), pygame.SRCALPHA)

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.background, (0, 0))

        self.box.fill((0, 0, 0, 0))
        box_thickness = 3
        pygame.draw.rect(self.box, self.GREEN, self.box.get_rect(), box_thickness)

        print("Connected to Tello Simulator")

    def streamon(self):
        print("Streaming on...")
    
    def check_screen_background_pathImage_box(func): # type: ignore
        def wrapper(self):
            if self.screen is not None and \
                self.background is not None and\
                self.path_image is not None and\
                self.box is not None:
                pass # nothing to do here, everything is already set up.
            else:
                print("TelloSimulator is not 'connect()'ed successfully")
                print("'connect()'ing internally")
                self.connect()
            return func(self) # type: ignore
        return wrapper
    
    @check_screen_background_pathImage_box # type: ignore
    def __render_box(self):
        # if not (self.background is None  or  self.screen is None):
        # clear the screen
        self.screen.blit(self.background, (0, 0)) # type: ignore

        self.yv = self.yv % 360  # Keep angle between 0 and 360 degrees
        b_z_size = ((1 + self.ud) * self.WINDOW_WIDTH, (1 + self.ud) * self.WINDOW_HEIGHT)  # Calculate box size based on drone's up/down movement
        
        ''''''
        surf_path = pygame.Surface((self.WINDOW_WIDTH,self.WINDOW_HEIGHT), pygame.SRCALPHA)
        surf_path.blit(self.path_image, (0,0)) # type: ignore

        rect = surf_path.get_rect(center=(self.lr,self.fb)) 
        old_center = rect.center  
        surf_path = pygame.transform.scale(surf_path, b_z_size) 
        surf_path = pygame.transform.rotate(surf_path , self.yv) 
        
        rect = surf_path.get_rect()  
        rect.center = old_center  

        # Draw the path image and the box (drone) on the screen
        self.screen.blit(surf_path, rect) # type: ignore
        self.screen.blit(self.box, self.box.get_rect(center=(self.DRONE_INIT_X, self.DRONE_INIT_Y))) # type: ignore

        ''''''

        '''
        # Resize and rotate the path image based on drone's orientation and size
        self.path_image = pygame.transform.scale(self.path_image, b_z_size) 
        self.path_image = pygame.transform.rotate(self.path_image, self.yv) 

        # Position the path image at the drone's current position
        self.path_image_rect = self.path_image.get_rect(center=(self.lr, self.fb))  

        # Draw the path image and the box (drone) on the screen
        self.screen.blit(self.path_image, self.path_image_rect)
        self.screen.blit(self.box, self.box.get_rect(center=(self.DRONE_INIT_X, self.DRONE_INIT_Y)))
        '''
    def send_rc_control(self,a:int, b:int, c:int, d:int):
        a *= -1 # because Tello() is oriented that way
        if not self.tookoff:
            # the drone has not yet taken off, so increasing sensitivity to make it easier for navigation
            self.lr += a*self.sensitivity*10
            self.fb += b*self.sensitivity*10
        self.lr += a*self.sensitivity
        self.fb += b*self.sensitivity
        self.ud += c*self.sensitivity*0.05
        self.yv += d
        # print(self.lr, self.fb, self.ud, self.yv)
        if (self.ud <= -0.99): self.ud = -0.99

        # print(f"Sending {a} - {b} - {c} - {d}")

        self.__render_box()

    @check_screen_background_pathImage_box # type: ignore
    def get_frame_read(self):
        # convert the surface to a numpy array
        array = pygame.surfarray.array3d(self.screen) # type: ignore
        image = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)

        # get the image under the Rectangle (Box)
        image_under = image[self.BOX_X :self.BOX_X+self.BOX_WIDTH,self.BOX_Y:self.BOX_Y+self.BOX_HEIGHT:]
        image_under = cv2.flip(cv2.rotate(image_under, cv2.ROTATE_90_CLOCKWISE), 1)
        
           
        pygame.display.flip()
        return image_under
       
    def take_off(self):
        if not self.tookoff:
            self.tookoff = True

            print("Taking off...")
    
    def land(self):
        if self.tookoff:
            print("Landing...")
        self.tookoff = False
    
    def move_forward(self, dist:int):
        if self.tookoff:
            self.send_rc_control(0, dist, 0, 0)

    def move_back(self, dist:int):
        if self.tookoff:
            self.send_rc_control(0, - dist, 0, 0)

    def move_left(self, dist:int):
        if self.tookoff:
            self.send_rc_control(- dist, 0, 0, 0)

    def move_right(self, dist:int):
        if self.tookoff:
            self.send_rc_control(dist, 0, 0, 0)

    def move_up(self, dist:int):
        if self.tookoff:
            self.send_rc_control(0, 0, dist, 0)
        
    def move_down(self, dist:int):
        if self.tookoff:
            self.send_rc_control(0, 0, - dist, 0)

    def rotate_clockwise(self, ang:int):
        if self.tookoff:
            ang *= 2 # 360 degree is 720 turns
            self.send_rc_control(0, 0, 0, ang)
    
    def rotate_counter_clockwise(self, ang:int):
        if self.tookoff:
            ang *= 2 # 360 degree is 720 turns
            self.send_rc_control(0, 0, 0, - ang)

    # def 
    

