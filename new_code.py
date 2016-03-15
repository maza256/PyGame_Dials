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





    throt_dem = myFont.render(str(throttle_demand), 5, GREEN, BACKGROUND_COLOUR)
    press_read = myFont.render(str(pressure_reading), 5, GREEN, BACKGROUND_COLOUR)
    n1_sped = myFont.render(str(n1_speed), 5, GREEN, BACKGROUND_COLOUR)
    temp_read = myFont.render(str(temp_reading), 5, GREEN, BACKGROUND_COLOUR)
    amb_press = myFont.render(str(ambient_pressure), 5, GREEN, BACKGROUND_COLOUR)



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

