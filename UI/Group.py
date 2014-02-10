__author__ = 'dark-wizard'

import pygame, UI


class Group():
    cbList = None
    screen = None
    selected = None

    def __init__(self, arr, vals, height):
        self.cbList = list()
        self.screen = pygame.display.get_surface()
        width = self.screen.get_width()
        k = 0
        block_width = width / len(arr)
        for x in arr:
            tmp = UI.Checkbox.Checkbox(x, 0, 0, 0)
            self.cbList.append(UI.Checkbox.Checkbox(x, block_width * k + (block_width - tmp.rect.width) / 2, height, vals[k]))
            self.screen.blit(self.cbList[k].image, self.cbList[k].rect)
            k += 1

    def clearAllCheckboxes(self):
        for x in self.cbList:
            x.setValue(False)

    def checkPress(self, evt, pos):
        for x in self.cbList:
            if x.rect.collidepoint(pos):
                self.clearAllCheckboxes()
                x.catch(evt)
                #print "%s selected!" % x.value
                self.selected = x.value