from GameUI.Town import Town

__author__ = 'dark-wizard'

import pygame
from GameMechanics.ColorPalette import ColorPalette as Palette
from GameMechanics.GameInfo import GameInfo as GI
from GameMechanics.ButtonWindowManager import ButtonWindowManager
#default size is 3 columns x 10 rows x 32 pixels
#default position: (0, 0)


class UnitGridRenderer():
    image = None
    panel = None
    storage = list()

    cornerPosition = (0, 0)
    COLUMNS = 3
    ROWS = 10
    defaultSize = pygame.Rect(cornerPosition, (COLUMNS*32, ROWS*32))
    cellSize = (32, 32)
    cellRect = pygame.Rect(cornerPosition, cellSize)

    def __init__(self, data_provider):
        self.image = pygame.Surface((self.COLUMNS * 32, self.ROWS * 32))
        self.redraw(data_provider)

    def redraw(self, data_provider):
        self.storage = data_provider
        #print self.storage
        panel = pygame.Surface((self.COLUMNS * 32, self.ROWS * 32))
        for i in range(self.COLUMNS * self.ROWS):
            data = None
            if i < len(data_provider) and not data_provider[i] is None:
                data = data_provider[i].image
            else:
                self.storage.append(None)
            s = self.drawCell(data)

            xpos, ypos = (i % self.COLUMNS) * self.cellSize[0], (i / self.COLUMNS) * self.cellSize[0]
            #print xpos, ypos
            panel.blit(s, pygame.Rect((xpos, ypos), self.cellSize))

        self.image = pygame.Surface((self.COLUMNS * 32, self.ROWS * 32))
        self.image.blit(panel, self.cornerPosition)

    def calc_press(self, pos):
        xcell, ycell = pos[0] / 32, pos[1] / 32
        cell_num = ycell * 3 + xcell
        selected = self.storage[cell_num]
        #print "clicked on unit grid, cell(%d, %d), unit: %s" % (xcell, ycell, selected)
        
        if not selected is None:
            #--backdoor for town
            if isinstance(selected, Town):
                GI.selected_town = selected
                GI.worldGrid.redraw(clearing=True)
                if not GI.selected_town.unit_inside is None:
                    GI.window_manager.set_leave_disabled(False)
                    GI.window_manager.set_enter_disabled(True)
                else:
                    GI.window_manager.set_leave_disabled(True)
                    GI.window_manager.set_enter_disabled(False)

                GI.game_core.center_camera(selected.position)
                GI.window_manager.show_right_panel()
                return
            #--end
            GI.selected_unit = selected
            GI.window_manager.show_unit_panel(selected)
            GI.game_core.center_camera(GI.selected_unit.position, True)
            GI.game_core.calc_all_areas()

    def cut_list(self, l):
        res = list()
        for x in l:
            if not x is None:
                res.append(x)
        return res

    def add_unit(self, unit):
        tmp = self.cut_list(self.storage)
        if len(tmp) < self.COLUMNS * self.ROWS:
            tmp.append(unit)
            #unit.hidden = False
            self.redraw(tmp)
        else:
            GI.window_manager.show("You can't acquire more soldiers!")

    def remove_unit(self, unit):
        tmp = self.cut_list(self.storage)
        if unit in tmp:
            tmp.remove(unit)
            #unit.hidden = True
            self.redraw(tmp)

    def drawCell(self, src):
        s = pygame.Surface(self.cellSize)
        if src is None:
            pygame.draw.rect(s, Palette.gray, self.cellRect)
            #s.fill(self.gray)
        else:
            s.blit(src, self.cornerPosition)
        pygame.draw.rect(s, Palette.black, self.cellRect, 2)

        return s
