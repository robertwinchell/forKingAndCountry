from GameUI import Unit

__author__ = 'dark-wizard'


class Knight(Unit.Unit):
    def __init__(self, pos):
        self.attack = 25
        self.defense = 2
        self.attack_range = 1
        self.movement = 5
        self.health = 30
        self.actual_health = 30
        Unit.Unit.__init__(self, "knt1", pos)
        self.display_name = "Knight"
