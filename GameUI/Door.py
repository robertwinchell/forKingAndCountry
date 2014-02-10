__author__ = 'dark-wizard'

import ActiveTile
from GameMechanics.GameInfo import GameInfo as GI


class Door(ActiveTile.ActiveTile):
    armor = 1000
    crashed = False

    def __init__(self, pos):
        ActiveTile.ActiveTile.__init__(self, "images/door.png", pos)

    def damage(self, dmg):
        self.armor -= dmg
        self.update_info()

    def set_crashed(self, value):
        self.crashed = value
        self.update_info()

    def update_info(self, who_checks=None):
        self.info = "castle door (%s). \nArmor: %d; \ncrashed: %d; " \
                    % (self.name, self.armor, self.crashed)
        self.info += "\nis friendly: %d" % int(GI.active_player == self.player_index)