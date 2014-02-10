from GameUI import Unit

__author__ = 'dark-wizard'


class Thief(Unit.Unit):
    def __init__(self, pos):
        self.attack = 1
        self.defense = 1
        self.attack_range = 1
        self.movement = 14
        self.health = 15
        self.actual_health = 15
        Unit.Unit.__init__(self, "thf2", pos)
        self.display_name = "Scout"