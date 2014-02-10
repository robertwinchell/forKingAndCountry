#!/usr/bin/env python

import random, os.path

#import basic pygame modules
import pygame
from pygame.locals import *
    
def load_sound(file):
    if not pygame.mixer: return dummysound()
    file = os.path.join(file)
    try:
        sound = pygame.mixer.Sound("sounds/"+ file +".wav")
        return sound
    except pygame.error:
        print ('Warning, unable to load, %s' % file)
    return dummysound()

def play(sound, queue=False):
    chanel = pygame.mixer.Channel(0)
    if queue:
        chanel.queue(sound)
    else:
        chanel.play(sound)

def play_bg(sound, mute = False):
    chanel = pygame.mixer.Channel(1)
    if not mute:
        chanel.play(sound, loops = -1)
    else:
        chanel.pause()

class dummysound:
    def play(self): pass


