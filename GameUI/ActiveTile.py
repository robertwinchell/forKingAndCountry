__author__ = 'dark-wizard'

import pygame, Tile
from GameMechanics.ColorPalette import ColorPalette as Palette


class ActiveTile(Tile.Tile):
    is_friendly = 0         # 0 - hostile, 1 - neutral, 2 - friendly
    player_index = -1
    base_name = "active tile"
    link = ""
    hidden = False
    source_surface = None

    def __init__(self, image_link, pos):
        self.link = image_link
        Tile.Tile.__init__(self, image_link, pos)

        self.source_surface = pygame.Surface((self.WIDTH, self.WIDTH), flags=pygame.SRCALPHA)
        #print self.image.get_at((0, 0))
        self.source_surface.blit(self.image, (0, 0))
        self.set_friendly(1)

        self.update_info(self.info + "\nis friendly:%s\nbelongs to (player):%s" % (self.is_friendly, self.player_index))

    def set_friendly(self, value):
        self.is_friendly = value
        self.image = pygame.Surface((self.WIDTH, self.WIDTH))
        if self.is_friendly == 2:
            self.image.blit(pygame.image.load("images/friendly_highlight.png").convert_alpha(), (0, 0))
        elif self.is_friendly == 0:
            self.image.blit(pygame.image.load("images/enemy_highlight.png").convert_alpha(), (0, 0))
        else:
            self.image.blit(pygame.image.load("images/neutral_highlight.png").convert_alpha(), (0, 0))
        self.image.blit(self.source_surface, (0, 0))
        self.update_source()