#!/usr/bin/python
"""
* gui.py
* 
* Created on: 1 Nov 2010
* Author:     Duncan Law
*
* Modified on: 9 Feb 2016
* Modified by: Marek Stefanowski
*
* Copyright (C) 2010 Duncan Law
* This program is free software; you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation; either version 2 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program; if not, write to the Free Software
* Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
* This program is free software; you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation; either version 2 of the License, or
* (at your option) any
* Requires pyGame to run.
* http://www.pygame.org

"""
import math
import pygame
from pygame.locals import *
import sys

class Dial:
    """
    Generic dial type.
    """
    def __init__(self, image, frameImage, x=0, y=0, w=0, h=0):
       """
       x,y = coordinates of top left of dial.
       w,h = Width and Height of dial.
       """
       self.x = x 
       self.y = y
       self.image = image
       self.frameImage = frameImage
       self.dial = pygame.Surface(self.frameImage.get_rect()[2:4])
       self.dial.fill((255,255,0))
       if(w==0):
          w = self.frameImage.get_rect()[2]
       if(h==0):
          h = self.frameImage.get_rect()[3]
       self.w = w
       self.h = h
       self.pos = self.dial.get_rect()
       self.pos = self.pos.move(x, y)

    def position(self, x, y):
        """
        Reposition top,left of dial at x,y.
        """
        self.x = x 
        self.y = y
        self.pos[0] = x 
        self.pos[1] = y 

    def position_center(self, x, y):
        """
        Reposition centre of dial at x,y.
        """
        self.x = x
        self.y = y
        self.pos[0] = x - self.pos[2]/2
        self.pos[1] = y - self.pos[3]/2

    def rotate(self, image, angle):
        """
        Rotate supplied image by "angle" degrees.
        This rotates round the centre of the image. 
        If you need to offset the centre, resize the image using self.clip.
        This is used to rotate dial needles and probably doesn't need to be used externally.
        """
        tmpImage = pygame.transform.rotate(image ,angle)
        imageCentreX = tmpImage.get_rect()[0] + tmpImage.get_rect()[2]/2
        imageCentreY = tmpImage.get_rect()[1] + tmpImage.get_rect()[3]/2

        targetWidth = tmpImage.get_rect()[2]
        targetHeight = tmpImage.get_rect()[3]

        imageOut = pygame.Surface((targetWidth, targetHeight))
        imageOut.fill((255,255,0))
        imageOut.set_colorkey((255,255,0))
        imageOut.blit(tmpImage,(0,0), pygame.Rect( imageCentreX-targetWidth/2,imageCentreY-targetHeight/2, targetWidth, targetHeight ) )
        return imageOut

    def clip(self, image, x=0, y=0, w=0, h=0, oX=0, oY=0):
        """
        Cuts out a part of the needle image at x,y position to the correct size (w,h).
        This is put on to "imageOut" at an offset of oX,oY if required.
        This is used to centre dial needles and probably doesn't need to be used externally.       
        """
        if(w==0):
           w = image.get_rect()[2]
        if(h==0):
           h = image.get_rect()[3]
        needleW = w + 2*math.sqrt(oX*oX)
        needleH = h + 2*math.sqrt(oY*oY)
        imageOut = pygame.Surface((needleW, needleH))
        imageOut.fill((255,255,0))
        imageOut.set_colorkey((255,255,0))
        imageOut.blit(image, (needleW/2-w/2+oX, needleH/2-h/2+oY), pygame.Rect(x,y,w,h))
        return imageOut

    def overlay(self, image, x, y, r=0):
        """
        Overlays one image on top of another using (255,255,0) (Yellow) as the overlay colour.
        """
        x -= (image.get_rect()[2] - self.dial.get_rect()[2])/2
        y -= (image.get_rect()[3] - self.dial.get_rect()[3])/2
        image.set_colorkey((255,255,0))
        self.dial.blit(image, (x,y))

class Generic(Dial):
    """
    Generic Dial. This is built on by other dials.
    """
    def __init__(self, x=0, y=0, w=0, h=0):
        """
        Initialise dial at x,y.
        Default size of 300px can be overidden using w,h.       
        """
        self.image = pygame.image.load('resources/AirSpeedNeedle.png').convert()
        self.frameImage = pygame.image.load('resources/Indicator_Background.png').convert()
        Dial.__init__(self, self.image, self.frameImage, x, y, w, h)
    def update(self, screen, angleX, iconLayer=0):
        """
        Called to update a Generic dial.
        "angleX" and "angleY" are the inputs.
        "screen" is the surface to draw the dial on.       
        """
        angleX %= 360
        angleX = 360 - angleX
        tmpImage = self.clip(self.image, 0, 0, 0, 0, 0, -35)
        tmpImage = self.rotate(tmpImage, angleX)
        self.overlay(self.frameImage, 0,0)
        if iconLayer:
          self.overlay(iconLayer[0],iconLayer[1],iconLayer[2])
        self.overlay(tmpImage, 0, 0)
        self.dial.set_colorkey((255,255,0))
        screen.blit( pygame.transform.scale(self.dial,(self.w,self.h)), self.pos )

class Specific_Dial(Generic):
    """
    Build a dial.
    """
    def __init__(self, x=0, y=0, w=0, h=0, resource='resources/battery2.png'):
        """
        Initialise dial at x,y.
        Default size of 300px can be overidden using w,h.
        """
        self.icon = pygame.image.load('resources/battery2.png').convert()
        Generic.__init__(self, x, y, w, h)
        self.frameImage = pygame.image.load(resource).convert()
    def update(self, screen, angleX=0):
        """
        Called to update a Battery dial.
        "angleX" is the input.
        "screen" is the surface to draw the dial on.       
        """
        if angleX > 100:
          angleX = 100
        elif angleX < 0:
          angleX = 0
        angleX *= 2.7
        angleX -= 135
        Generic.update(self, screen, angleX, (self.icon, 0, 100))

def screen_init(Xres = 800, Yres = 480, BACKGROUND_COLOUR=(55, 55, 55)):
    pygame.init()
    # Initialise screen.
    screen = pygame.display.set_mode((Xres, Yres), pygame.FULLSCREEN)
    screen.fill(BACKGROUND_COLOUR)
    return screen

