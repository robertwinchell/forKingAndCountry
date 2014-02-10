from GameUI import Unit

__author__ = 'dark-wizard'


class Archer(Unit.Unit):
    def __init__(self, pos):
        self.attack = 10
        self.defense = 3
        self.attack_range = 3
        self.movement = 7
        self.health = 20
        self.actual_health = 20
        Unit.Unit.__init__(self, "avt1", pos)
        self.display_name = "Archer"
