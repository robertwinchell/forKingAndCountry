__author__ = 'dark-wizard'
import GameUI
import pygame


class Placeholder(GameUI.ActiveTile.ActiveTile):
    link_to_obj = None

    def __init__(self, pos, link):
        self.link_to_obj = link
        #self.position = pos
        GameUI.ActiveTile.ActiveTile.__init__(self, "images/placeholder.png", pos)