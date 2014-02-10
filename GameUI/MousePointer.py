__author__ = 'dark-wizard'

import pygame, Tile


class MousePointer(Tile.Tile):
    def __init__(self):
        Tile.Tile.__init__(self, "images/mouse.png", (0, 0))