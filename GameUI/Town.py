from GameUI.ActiveTile import ActiveTile

__author__ = 'dark-wizard'


class Town(ActiveTile):
    loyalty = 0
    unit_inside = None
    can_recruit = True
    copy = True

    WIDTH = 64

    def __init__(self, pos):
        ActiveTile.__init__(self, "images/town.gif", pos)

    def mod_loyalty(self, value):
        value = int(value)
        self.loyalty += value
        if self.loyalty > 100:
            self.loyalty = 100
        if self.loyalty < 0:
            self.loyalty = 0

    def update_info(self, args=None):
        if not args is None:
            self.info = args
        info = "unit_inside:%s\nhas soldiers:%s\nloyalty:%s\n" % (self.unit_inside, self.can_recruit, self.loyalty)
        self.info = info
