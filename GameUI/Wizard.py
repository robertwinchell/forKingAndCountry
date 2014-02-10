from GameUI import Unit

__author__ = 'dark-wizard'


class Wizard(Unit.Unit):
    def __init__(self, pos):
        self.attack = 15
        self.defense = 1
        self.attack_range = 3
        self.movement = 4
        self.health = 15
        self.actual_health = 15
        Unit.Unit.__init__(self, "amg1", pos)
        self.display_name = "Wizard"
