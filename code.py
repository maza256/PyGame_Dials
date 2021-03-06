#!/usr/bin/python
from gui import *
from random import randint
import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
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

#to use the dimmer:
def eec_off():
    dimmer = Dimmer(keepalive=1)
    dimmer.dim(darken_factor=128, color_filter=(0,0,0))
    time.sleep(1)
    dimmer.undim()

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)
 
        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low
 
        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
 
        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1
 
        GPIO.output(cspin, True)
        
        adcout >>= 1       # first bit is 'null' so drop it
	set_val = adcout / 10.24           # convert 10bit adc0 (0-1024) trim pot read into 0-100 Resistance level
	set_val = round(set_val)          # round out decimal value
	set_val = int(set_val)            # cast Resistance as integer

        return set_val
# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25
 
# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT) #Potentiometer MOSI
GPIO.setup(SPIMISO, GPIO.IN) 
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)
GPIO.setup (14, GPIO.OUT) #Buzzer
GPIO.setup (4, GPIO.IN)    #Push buttons
GPIO.setup (17, GPIO.IN)    #Push buttons
GPIO.setup (22, GPIO.IN)   #Push buttons
GPIO.setup (27, GPIO.IN)   #Push buttons
GPIO.setup (5, GPIO.OUT) #LED g1
GPIO.setup (6, GPIO.OUT) #LED g2
GPIO.setup (7, GPIO.OUT)  #LED g3
GPIO.setup (12, GPIO.OUT) #LED g4
GPIO.setup (13, GPIO.OUT) #LED g5
GPIO.setup (16, GPIO.OUT) #LED r6
GPIO.setup (19, GPIO.OUT) #LED r7
GPIO.setup (20, GPIO.OUT) #LED r8
GPIO.setup (21, GPIO.OUT) #LED r9
GPIO.setup (26, GPIO.OUT) #LED r10
GPIO.setup (8, GPIO.IN)   # Switch 3
GPIO.setup (9, GPIO.IN)   # Switch 1.2 (up)
GPIO.setup (10, GPIO.IN)  # Switch 1.1 (down)
GPIO.setup (11, GPIO.IN)  # Switch 2

frequency = 0.1 #buzzer
timer = 10  #buzzer
maxvalue = 70  #buzzer

def buzzersounding():
    for I in range(0, timer):
        GPIO.output (14, True)
        time.sleep (frequency)
        GPIO.output (14, False) 
        time.sleep (frequency)

 
# 10k trim pot connected to adc #0
TRA = 0;
N2 = 1;
P2o = 2;
TGT = 3;
Po = 4;
#end of potentiometer setup

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
pressure = Specific_Dial(0,240,DIAL_WIDTH, DIAL_HEIGHT,'resources/pressure.png')
speed = Specific_Dial(200,240,DIAL_WIDTH, DIAL_HEIGHT, 'resources/percentage.png')
temp = Specific_Dial(400,240,DIAL_WIDTH, DIAL_HEIGHT, 'resources/temperature.png')
ambPressure = Specific_Dial(600,240,DIAL_WIDTH, DIAL_HEIGHT, 'resources/pressure.png')
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
            GPIO.cleanup()
            sys.exit()   # end program.
    #Second test for quitting in fullscreen
    if pygame.mouse.get_pressed()[0]:
        counter = counter + 1
        print counter
        if counter > 5:
            print "Mouse Exit..."
            GPIO.cleanup()
            sys.exit() #end program

    #buzzer
    #if not GPIO.input (4) or not GPIO.input (17) or not GPIO.input (22) or not GPIO.input (27): 
        
#	print "buzzer"

 #   if value<maxvalue:
  #      buzzersounding

    if not GPIO.input (4):
        GPIO.output (16,True)    #pushbutton1
	GPIO.output(5, False)
        screen.blit(i_warning_on,(400,5))
        screen.blit(i_extinguish_on,(400, 164))	
        pygame.display.update()
	for x in range(0, 3):
            GPIO.output (14, True)
	    time.sleep(0.5)
            GPIO.output (14, False)
	    time.sleep(0.5)
        screen.blit(i_warning_off,(400,5))
        screen.blit(i_extinguish_off,(400, 164))	

    else:
	GPIO.output (5,True)
	GPIO.output(16,False)

    if not GPIO.input (17):
        GPIO.output (19,True) #pushbutton2
        GPIO.output (6,False) 
    else:
	GPIO.output (6,True)
	GPIO.output (19,False)

    if not GPIO.input (22):
        GPIO.output (20,True)  #pushbutton3
        GPIO.output (7,False)
    else:
        GPIO.output (7,True)
	GPIO.output (20,False) 

    if not GPIO.input (27):
        GPIO.output (21,True)  #pushbutton4
        GPIO.output (12,False)
    else:
	GPIO.output (12,True)
	GPIO.output (21, False)

    if GPIO.input (9):
    	screen.blit(chanA, chan_Rect)    
    if GPIO.input (10):

    	screen.blit(chanB, chan_Rect)


    #Sets FPS, number of times this will run per second.
    #Lower number is slower
    clock.tick(5)


    
  

#Temporary default values, to be replace with calculations and data reads
    # read the analog pin
    throttle_demand = readadc(TRA, SPICLK, SPIMOSI, SPIMISO, SPICS)
    shaft_speed = readadc(N2, SPICLK, SPIMOSI, SPIMISO, SPICS)
    pressure20 = readadc(P2o, SPICLK, SPIMOSI, SPIMISO, SPICS)
    turbine_gas_temp = readadc(TGT, SPICLK, SPIMOSI, SPIMISO, SPICS)
    pressure0 = readadc(Po, SPICLK, SPIMOSI, SPIMISO, SPICS)
	


#algorithm code goes here


    throttle_demand = throttle_demand
    pressure_reading = pressure20
    n1_speed = shaft_speed
    temp_reading = turbine_gas_temp
    ambient_pressure = pressure0
    sixth_dial_read = 0

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
