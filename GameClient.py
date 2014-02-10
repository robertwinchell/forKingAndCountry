__author__ = 'dark-wizard'

import pygame, sys
from GameMechanics import GameCoreManager
from GameMechanics import *
from GameMechanics.GameInfo import GameInfo as GI
import GameUI

lore = """
With the death of the King comes
the infighting among his sons.
He failed to specify an heir and now
you must defeat your brother and
claim the kingdom. Take over all 
of your brother's territory and
force his surrender or just kill 
him and be done with it!        
"""

class GameClient():
    screen = None
    unitGrid = None
    worldGrid = None
    background = None
    game_core = None

    test_AI = None

    clock = pygame.time.Clock()

    def __init__(self, size, conf, anim):
        pygame.init()
        self.anim = anim 
        #self.screen = pygame.display.set_mode((640, 480))
        self.screen = pygame.display.set_mode((640, 480), pygame.FULLSCREEN)
        self.loadSprites(size, conf)
        self.run_forever()

    def loadSprites(self, size, conf):
        self.unitGrid = GameUI.UnitGridRenderer.UnitGridRenderer([])
        self.worldGrid = GameUI.WorldRenderer.WorldRenderer(size)
        #add call for generating "new game" objects
        self.background = pygame.image.load("images/bg.jpg").convert()
        self.game_core = GameCoreManager.GameCoreManager(2, (size, size + 6))

        start = 1
        if conf == "PvP":
            start = -1
        self.test_AI = AI.AIManager(start)

        self.create_links_to_static()

        GI.game_core.new_game()
        GI.game_core.create_backup()
        GI.worldGrid.draw_active_data(GI.all_active_data)
        GI.window_manager.show(lore, header = "The King is dead!\n")

        #GI.selected_unit = GI.worldGrid.get_block(4, 0)

    def redraw(self):
        self.screen.blit(self.background, (0, 0))
        
        if GI.window_manager.tl_active and not GI.ai.working or (GI.ai.working and GI.ai.need_to_redraw):
            self.game_core.move_obj()
        if GI.ai.need_to_switch:
            GI.ai.load_next_unit()
        if GI.ai.working and not self.anim:
            return
                
        self.worldGrid.redraw()
        #self.worldGrid.draw_active_data(GI.all_active_data)
        self.worldGrid.update_position()
        #self.screen.blit(self.worldGrid.image, self.worldGrid.world_position)
        self.screen.blit(self.unitGrid.image, self.unitGrid.cornerPosition)

        GI.window_manager.redraw()
        self.screen.blit(GI.window_manager.image, (0, 0))

        pygame.display.update()
        pygame.display.flip()

    def create_links_to_static(self):
        GI.worldGrid = self.worldGrid
        GI.game_core = self.game_core
        GI.unitGrid = self.unitGrid
        GI.ai = self.test_AI
        #print GI.ai

        windows = ButtonWindowManager.ButtonWindowManager()
        GI.window_manager = windows

        GI.set_defaults()

    def processEvents(self, event):
        res = GI.window_manager.process_event(event)
        if res:
            self.worldGrid.process_event(event)
        if event.type is pygame.QUIT or event.type is pygame.K_q:
            pygame.quit()
            sys.exit()

    def run_forever(self):
        while 1:
            GI.time_passed = self.clock.tick(20000)
            #print GI.time_passed
            for event in pygame.event.get():
                self.processEvents(event)
            self.redraw()

if __name__ == "__main__":
    gl = GameClient()
