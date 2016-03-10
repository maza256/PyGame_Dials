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

frequency = 0.5 #buzzer
time = 10  #buzzer
maxvalue = 70  #buzzer

def buzzersounding():
    for I in range(0, time):
        GPIO.OUTPUT (14, True)
        time.sleep (frequency)
        GPIO.OUTPUT (14, False) 
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
i_fuelpump_on       = pygame.image.load('resources/fuel_pumps_on.png')
i_fuelpump_off      = pygame.image.load('resources/fuel_pumps_off.png')
i_flameout_on       = pygame.image.load('resources/flameout_on.png')
i_flameout_off      = pygame.image.load('resources/flameout_off.png')
i_vibration_on      = pygame.image.load('resources/vibration_on.png')
i_vibration_off    = pygame.image.load('resources/vibration_off.png')
i_surge_on          = pygame.image.load('resources/surge_on.png')
i_surge_off         = pygame.image.load('resources/surge_off.png')
i_ice_on            = pygame.image.load('resources/ice_on.png')
i_ice_off           = pygame.image.load('resources/ice_off.png')

# Initialise Dials.
#(X Co-od, Y Co-od, Width, Heigth, image resource)
throttle = Specific_Dial(0,0,DIAL_WIDTH, DIAL_HEIGHT, 'resources/percentage.png')
pressure = Specific_Dial(0,240,DIAL_WIDTH, DIAL_HEIGHT,'resources/pressure.png')
speed = Specific_Dial(200,240,DIAL_WIDTH, DIAL_HEIGHT, 'resources/percentage.png')
temp = Specific_Dial(400,240,DIAL_WIDTH, DIAL_HEIGHT, 'resources/temperature.png')
ambPressure = Specific_Dial(600,240,DIAL_WIDTH, DIAL_HEIGHT, 'resources/pressure.png')
clock = pygame.time.Clock()

#Font for text
myFont = pygame.font.SysFont("monospace", 36)
myFont.set_bold(True)

#Set locations for each of the warning panel images. All off to begin with.
screen.blit(i_warning_off,(205, 5))
screen.blit(i_extinguish_off,(400, 5))
screen.blit(i_flameout_off, (205, 164))
screen.blit(i_fuelpump_off,(600, 5))
screen.blit(i_vibration_off,(205, 85))
screen.blit(i_surge_off,(400, 85))
screen.blit(i_ice_off,(600, 85))

#Label to display Channel A and Channel B
chanA = myFont.render("Channel A", 5, GREEN, BACKGROUND_COLOUR)
chanB = myFont.render("Channel B", 1, LIGHT_BLUE, BACKGROUND_COLOUR)

chan_Rect = chanA.get_rect()
chan_Rect.centerx = 520
chan_Rect.centery = 195

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


    if GPIO.input (4) or GPIO.input (17) or GPIO.input (22) or GPIO.input (27):  #buzzer
        buzzersounding

 #   if value<maxvalue:
  #      buzzersounding

    if GPIO.input (4):
        GPIO.output (16,True)    #pushbutton1
	GPIO.output(5, False)
    else:
	GPIO.output (5,True)
	GPIO.output(16,False)

    if GPIO.input (17):
        GPIO.output (19,True) #pushbutton2
        GPIO.output (6,False) 
    else:
	GPIO.output (6,True)
	GPIO.output (19,False)

    if GPIO.input (22):
        GPIO.output (20,True)  #pushbutton3
        GPIO.output (7,False)
    else:
        GPIO.output (7,True)
	GPIO.output (20,False) 

    if GPIO.input (27):
        GPIO.output (21,True)  #pushbutton4
        GPIO.output (12,False)
    else:
	GPIO.output (12,True)
	GPIO.output (21, False)

    

    #Sets FPS, number of times this will run per second.
    #Lower number is slower
    clock.tick(5)


    #Demo of how to activate the warning notices, simply switching on and off
    if test:
        screen.blit(i_warning_on,(205,5))
        test = False
    else:
        screen.blit(i_warning_off,(205,5))
        test = True
    
    if test:
       screen.blit(chanA, chan_Rect)
    else:
        screen.blit(chanB, chan_Rect)

#Temporary default values, to be replace with calculations and data reads
    # read the analog pin
    throttle_demand = readadc(TRA, SPICLK, SPIMOSI, SPIMISO, SPICS)
    shaft_speed = readadc(N2, SPICLK, SPIMOSI, SPIMISO, SPICS)
    pressure20 = readadc(P2o, SPICLK, SPIMOSI, SPIMISO, SPICS)
    turbine_gas_temp = readadc(TGT, SPICLK, SPIMOSI, SPIMISO, SPICS)
    pressure0 = readadc(Po, SPICLK, SPIMOSI, SPIMISO, SPICS)
	


#algorithm code goes here


    #Call to update all the dials with the new readings
    throttle.update(screen, throttle_demand)
    pressure.update(screen, pressure20)
    speed.update(screen, shaft_speed)
    temp.update(screen, turbine_gas_temp)
    ambPressure.update(screen, pressure0)
    #Call to redraw the screen to show the updates
    pygame.display.update()
