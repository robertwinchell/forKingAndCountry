__author__ = 'dark-wizard'
from GameMechanics.GameInfo import GameInfo as GI


class CastleProvider:
    units = list()

    def __init__(self, arr):
        for x in arr:
            self.units.append(x)

    def has_unit(self, x):
        if x in self.units:
            return True
        return False

    def add_unit(self, x):
        self.units.append(x)

    def remove_unit(self, x):
        #print unit in self.units_inside
        k = 0
        for unit in self.units:
            if unit == x:
                del self.units[k]

    def get_units(self):
        res = list()
        for x in self.units:
            if x.player_index == GI.active_player:
                res.append(x)
        return res

    def get_enemy_units(self):
        res = list()
        for x in self.units:
            if x.player_index != GI.active_player:
                res.append(x)
        return res