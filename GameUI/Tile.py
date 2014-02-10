__author__ = 'dark-wizard'

import pygame


class Tile():
    image = None
    src = None
    absolute_rect = None
    mark = 0
    label = 0

    skull_time = 0
    skull_surf = None

    walk_surf = None
    fight_surf = None

    position = None
    name = ""
    base_name = "cell"
    info = ""

    walkable = True
    walk_highlighted = False
    fight_highlighted = False

    WIDTH = 32

    def __init__(self, image_link, pos):
        self.image = pygame.Surface((self.WIDTH, self.WIDTH), flags=pygame.SRCALPHA)
        self.image.blit(pygame.image.load(image_link).convert_alpha(), (0, 0))
        self.src = self.image.copy()

        self.walk_surf = pygame.image.load("images/walk_highlight.png").convert_alpha()
        self.fight_surf = pygame.image.load("images/fight_highlight.png").convert_alpha()
        self.skull_surf = pygame.image.load("images/skull_and_bones.png").convert_alpha()

        #self.image = pygame.Surface((32, 32), flags=pygame.SRCALPHA)
        #self.image.blit(self.fight_surf, (0, 0))

        self.position = pos
        self.name = "%s%d_%d" % (self.base_name, pos[0], pos[1])
        self.update_info()
        #self.set_highlighted("fight")

    def get_rect(self):
        if not self.absolute_rect is None:
            return self.absolute_rect

        return pygame.Rect(self.position[0] * 32, self.position[1] * 32, self.WIDTH, self.WIDTH)

    def set_absolute_rect(self, r):
        self.absolute_rect = r

    def get_info(self):
        return self.info

    def update_info(self, args=None):
        if not args is None:
            self.info = args
            return
        self.info = "name:%s\nwalk_highlighted:%s\nfight_highlighted:%s" % (
            self.name, self.walk_highlighted, self.fight_highlighted)

    def update_source(self, new_image=None):
        #using, for example, when highlighting as friendly
        self.src = self.image.copy()
        if not new_image is None:
            self.src.blit(new_image, (0, 0))

    def set_highlighted(self, val, light = True):
        self.image = pygame.Surface((self.WIDTH, self.WIDTH), flags=pygame.SRCALPHA)
        self.image.blit(self.src, (0, 0))
        if self.skull_time > 0:
            self.image.blit(self.skull_surf, (0, 0))
            #print "skulls left for %d turns" % self.skull_time

        if val == "none" or val == "":
            self.fight_highlighted = self.walk_highlighted = False

        if val == "walk":
            #highlight as walking
            if light:
                self.image.blit(self.walk_surf, (0, 0))
            self.walk_highlighted = True

        if val == "fight":
            #highlight as walking
            if light:
                self.image.blit(self.fight_surf, (0, 0))
            self.fight_highlighted = True

        if val == "skull":
            #add bones
            self.image.blit(self.skull_surf, (0, 0))
            self.skull_time = 4
