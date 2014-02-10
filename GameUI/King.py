from GameUI import Unit, ActiveTile

__author__ = 'dark-wizard'


class King(Unit.Unit):
    def __init__(self, pos):
        self.attack = 25
        self.defense = 5
        self.attack_range = 1
        self.movement = 6
        self.health = 300
        self.actual_health = 300
        Unit.Unit.__init__(self, "kin1", pos)
        self.display_name = "King"
        self.update_info()
