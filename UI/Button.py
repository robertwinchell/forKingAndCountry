__author__ = 'dark-wizard'

import pygame
from GameMechanics.ColorPalette import ColorPalette as CP


class Button(pygame.sprite.Sprite):
    def __init__(self, image, x, y, color = CP.golden, alpha = False):
        self.image = pygame.Surface((96, 28))

        if alpha:
            self.image.fill(CP.gray)
            self.image.set_colorkey(CP.gray)
        
        pygame.draw.rect(self.image, color, pygame.Rect(0, 0, 96, 28), 2)
        
        self.txt = pygame.font.SysFont(None, 17, True).render(image, 3, color)
        
        self.image.blit(self.txt, ((96 - self.txt.get_width()) / 2, (28 - self.txt.get_height()) / 2))
        #self.image = pygame.image.load(image).convert_alpha()

        if x == "CENTER":
            x = (pygame.display.get_surface().get_width() - self.image.get_width())/2

        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect((x, y), self.image.get_size())

    def get_height(self):
        return self.image.get_height()

    def get_width(self):
        return self.image.get_width()

    def get_size(self):
        return self.image.get_size()
