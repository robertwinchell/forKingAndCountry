__author__ = 'dark-wizard'

import pygame, Button


class Checkbox(pygame.sprite.Sprite):
    checked = False
    content = None
    default = None
    value = None

    def __init__(self, image, x, y, value = False):
        pygame.sprite.Sprite.__init__(self)
        self.content = Button.Button(image, x, y)
        self.value = value

        self.image = self.content.image
        self.default = self.image
        self.rect = self.content.rect

    def setValue(self, value):
        #print "changing..."
        self.checked = value

        surf = pygame.display.get_surface()
        rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())

        s = surf.subsurface(self.rect)
        s.fill((0, 0, 0), rect)
        s.blit(self.image, rect)

        if self.checked:
            pygame.draw.rect(s, (0, 255, 255), rect, 3)

    def catch(self, e):
        if e.type == pygame.MOUSEBUTTONUP:
            self.setValue(not self.checked)