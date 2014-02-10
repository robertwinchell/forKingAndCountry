__author__ = 'dark-wizard'
import GameUI
from GameMechanics.GameInfo import GameInfo as GI


class Castle(GameUI.ActiveTile.ActiveTile):
    units_inside = None
    WIDTH = 64
    toughness = 1000
    shown_warning = False
    crashed = False

    def __init__(self, pos):
        GameUI.ActiveTile.ActiveTile.__init__(self, "images/castle.gif", pos)
        self.units_inside = GameUI.CastleProvider.CastleProvider(list())

    def add_unit_to_castle(self, unit):
        self.units_inside.add_unit(unit)
        if not self.shown_warning and not GI.ai.working:
            GI.window_manager.show("when unit is placed in the castle, \nit auto-attacks any enemy!\n"
                                   "To release unit, just select it from \nthe right menu of the castle")
            self.shown_warning = True

    def remove_unit_from_castle(self, unit):
        if self.units_inside.has_unit(unit):
            self.units_inside.remove_unit(unit)

    def has_unit(self, x):
        return self.units_inside.has_unit(x)

    def get_units(self, friendly=True):
        if friendly:
            return self.units_inside.get_units()
        else:
            return self.units_inside.get_enemy_units()

    def has_free_space(self):
        if len(self.units_inside.get_units()) < 9:
            return True
        return False

    def damage(self, dmg):
        self.toughness -= dmg
        if self.toughness <= 0:
            self.set_crashed(True)
        self.update_info()

    def set_crashed(self, value):
        self.crashed = value
        self.hidden = True
        self.update_info()

    def update_info(self, who_checks=None):
        self.info = "castle (%s). \nToughness: %d; \ncrashed: %d; " \
                    % (self.name, self.toughness, self.crashed)
        self.info += "\nis friendly: %d" % int(GI.active_player == self.player_index)