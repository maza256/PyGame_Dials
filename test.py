#!/usr/bin/python
from gui import *
from random import randint
import time
BACKGROUND_COLOUR = (55, 55, 55)
GREEN = (0, 255,0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
LIGHT_BLUE = (0, 100, 255)

#create a screen to draw on
#(Horizontal Resolution, Vertical Resolution, Red Fill Value, Green Fill Value, Blue Fill Value)
screen = screen_init(800, 480, (BACKGROUND_COLOUR))
DIAL_WIDTH = 200
DIAL_HEIGHT = 240

class Dimmer:
    def __init__(self, keepalive=0):
        self.keepalive=keepalive
        if self.keepalive:
            self.buffer=pygame.Surface(pygame.display.get_surface().get_size())
        else:
            self.buffer=None
        
    def dim(self, darken_factor=64, color_filter=(0,0,0)):
        if not self.keepalive:
            self.buffer=pygame.Surface(pygame.display.get_surface().get_size())
        self.buffer.blit(pygame.display.get_surface(),(0,0))
        if darken_factor>0:
            darken=pygame.Surface(pygame.display.get_surface().get_size())
            darken.fill(color_filter)
            darken.set_alpha(darken_factor)
            # safe old clipping rectangle...
            old_clip=pygame.display.get_surface().get_clip()
            # ..blit over entire screen...
            pygame.display.get_surface().blit(darken,(0,0))
            pygame.display.flip()
            # ... and restore clipping
            pygame.display.get_surface().set_clip(old_clip)

    def undim(self):
        if self.buffer:
            pygame.display.get_surface().blit(self.buffer,(0,0))
            pygame.display.flip()
            if not self.keepalive:
                self.buffer=None


def eec_off():
    dimmer = Dimmer(keepalive=1)
    dimmer.dim(darken_factor=128, color_filter=(0,0,0))
    time.sleep(1)
    dimmer.undim()

#Load in all the images that will be utilised for the warning panel
i_warning_on        = pygame.image.load('resources/warning_on.png')
i_warning_off       = pygame.image.load('resources/warning_off.png')
i_extinguish_on     = pygame.image.load('resources/extinguisher_on.png')
i_extinguish_off    = pygame.image.load('resources/extinguisher_off.png')
i_shaftbreak_on     = pygame.image.load('resources/shaftbreak_on.png')
i_shaftbreak_off    = pygame.image.load('resources/shaftbreak_off.png')
i_thrustreverse_on  = pygame.image.load('resources/thrustreverse_on.png')
i_thrustreverse_off = pygame.image.load('resources/thrustreverse_off.png')
i_ice_on            = pygame.image.load('resources/ice_on.png')
i_ice_off           = pygame.image.load('resources/ice_off.png')

# Initialise Dials.
#(X Co-od, Y Co-od, Width, Heigth, image resource)
throttle = Specific_Dial(0,0,DIAL_WIDTH, DIAL_HEIGHT, 'resources/percentage.png')
pressure = Specific_Dial(0,240,DIAL_WIDTH, DIAL_HEIGHT,'resources/percentage.png')
speed = Specific_Dial(200,240,DIAL_WIDTH, DIAL_HEIGHT, 'resources/percentage.png')
temp = Specific_Dial(400,240,DIAL_WIDTH, DIAL_HEIGHT, 'resources/percentage.png')
ambPressure = Specific_Dial(600,240,DIAL_WIDTH, DIAL_HEIGHT, 'resources/percentage.png')
sixth_dial = Specific_Dial(200,0, DIAL_WIDTH, DIAL_HEIGHT, 'resources/percentage.png')
clock = pygame.time.Clock()

#Font for text
myFont = pygame.font.SysFont("monospace", 36)
myFont.set_bold(True)

#Set locations for each of the warning panel images. All off to begin with.
screen.blit(i_warning_off,(400, 5))
screen.blit(i_extinguish_off,(400,164))
screen.blit(i_shaftbreak_off, (400, 85))
screen.blit(i_thrustreverse_off, (600, 164))
screen.blit(i_ice_off,(600, 85))

#Label to display Channel A and Channel B
chanA = myFont.render("Chan A", 5, GREEN, BACKGROUND_COLOUR)
chanB = myFont.render("Chan B", 1, LIGHT_BLUE, BACKGROUND_COLOUR)

chan_Rect = chanA.get_rect()
chan_Rect.centerx = 700
chan_Rect.centery = 20

test = True
label = None
counter = 0

# Main program loop.
while 1:
    #Check if close button has been pressed
    for event in pygame.event.get():
        if event.type == QUIT:
            print "Exiting...."
            sys.exit()   # end program.
    #Second test for quitting in fullscreen
    if pygame.mouse.get_pressed()[0]:
        counter = counter + 1
        print counter
        if counter > 10:
            print "Mouse Exit..."
            sys.exit() #end program
    

    #Sets FPS, number of times this will run per second.
    #Lower number is slower
    clock.tick(5)


    #Demo of how to activate the warning notices, simply switching on and off
    if test:
#        screen.blit(i_warning_on,(205,5))
        test = False
    else:
	screen.blit(i_warning_off,(400,5))
        eec_off()
	test = True
    
    if test:
       screen.blit(chanA, chan_Rect)
    else:
        screen.blit(chanB, chan_Rect)

#Temporary default values, to be replace with calculations and data reads
    throttle_demand = randint(0,100)
    pressure_reading = randint(0,100)
    n1_speed = randint(0,100)
    temp_reading = randint(0,100)
    ambient_pressure = randint(0,100)
    sixth_dial_read = randint(0, 100)

    throt_dem = myFont.render(str(throttle_demand), 5, GREEN, BACKGROUND_COLOUR)
    press_read = myFont.render(str(pressure_reading), 5, GREEN, BACKGROUND_COLOUR)
    n1_sped = myFont.render(str(n1_speed), 5, GREEN, BACKGROUND_COLOUR)
    temp_read = myFont.render(str(temp_reading), 5, GREEN, BACKGROUND_COLOUR)
    amb_press = myFont.render(str(ambient_pressure), 5, GREEN, BACKGROUND_COLOUR)
    six_dial = myFont.render(str(sixth_dial_read), 5, GREEN, BACKGROUND_COLOUR)


    #Call to update all the dials with the new readings
    throttle.update(screen, throttle_demand)
    screen.blit(throt_dem, (75, 190))
    pressure.update(screen, pressure_reading)
    screen.blit(press_read, (75, 430))
    speed.update(screen, n1_speed)
    screen.blit(n1_sped, (275, 430))
    temp.update(screen, temp_reading)
    screen.blit(temp_read, (475, 430))
    ambPressure.update(screen, ambient_pressure)
    screen.blit(amb_press, (675, 430))
    sixth_dial.update(screen, sixth_dial_read)
    screen.blit(six_dial, (275, 190))
    #Call to redraw the screen to show the updates
    pygame.display.update()
