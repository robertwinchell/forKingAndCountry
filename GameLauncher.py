__author__ = 'dark-wizard'

import pygame, sys
import UI
import GameClient
from GameMechanics.ColorPalette import ColorPalette as Palette
from GameMechanics.GameSound import *

class GameLauncher():
    screen = None
    btn = None
    group = None
    group2 = None
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480), pygame.FULLSCREEN)
        #self.screen = pygame.display.set_mode((640, 480))
        background = pygame.image.load("images/brick_wall.jpg")
        self.screen.blit(background, (0,0))
        self.loadSprites()
        self.run_forever()

    def loadSprites(self):
        
        title = pygame.font.Font("fonts/Flesh Wound.ttf", 60).render("For King And Country", 3, Palette.white)
        self.screen.blit(title, (( 640 - title.get_width())/2,50))

        self.music = UI.Checkbox.Checkbox("Music", 165 , 330)
        self.screen.blit(self.music.image, self.music.rect)

        self.ai_anim = UI.Checkbox.Checkbox("AI Animation", 378, 330)
        self.screen.blit(self.ai_anim.image, self.ai_anim.rect)

        self.btn = UI.Button.Button("Start Game!", "CENTER", 420)
        self.screen.blit(self.btn.image, self.btn.rect)

        self.group = UI.Group.Group(["30x30", "40x40", "50x50"], [30, 40, 50],  150)
        self.group2 = UI.Group.Group(["PvP", "PvAI"], ["PvP", "PvAI"],  240)

    def processEvents(self, event):
        pos = pygame.mouse.get_pos()

        if event.type in (pygame.QUIT, pygame.KEYDOWN):
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONUP:
            self.group.checkPress(event, pos)
            self.group2.checkPress(event, pos)

            if self.music.rect.collidepoint(pos):
                self.music.catch(event);
                self.turn_music(not self.music.checked)

            if self.ai_anim.rect.collidepoint(pos):
                self.ai_anim.catch(event);
                
            if self.btn.rect.collidepoint(pos):
                #pygame.display.iconify()
                size = self.group.selected
                conf = self.group2.selected
                anim = self.ai_anim.checked
                if size is None or conf is None:
                    return
                gc = GameClient.GameClient(size, conf, anim)

    def turn_music(self, state = False):
        music = load_sound("music")
        play_bg(music, state)
       
    def run_forever(self):
        while 1:
            for event in pygame.event.get():
                self.processEvents(event)
            pygame.display.update()
            pygame.time.delay(100)


if __name__ == "__main__":
    gl = GameLauncher()
