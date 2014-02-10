import GameUI
from random import randint

__author__ = "dark-wizard"

import pygame, random, copy
import Tile, ActiveTile, Door
from GameMechanics.GameInfo import GameInfo as GI


class WorldRenderer():
    image = None
    active_panel = None
    screen = None

    commonLandData = list()
    userActiveData = list()
    tile_width = 32
    active_user = 0

    world_map = list()
    active_map = list()

    grid_width = 0
    grid_height = 0

    world_position = (0, 0)
    world_speed = [0, 0]

    must_redraw = None
    need_to_redraw = True

    def __init__(self, size):
        self.grid_height = size
        self.grid_width = size + 6
        self.generate_land()

    def generate_static_object(self, x, y):
        r = randint(0,15)
        
        if r < 4 and r > 0:
            image_link = "images/tiles/" + r.__str__() +".png"
            walkable = False 
        else:
            image_link = "images/tiles/0.png"
            walkable = True
        
        s = Tile.Tile(image_link, (x, y))
        s.walkable = walkable
        return s

    def generate_land(self):
        for i in range(0, self.grid_height):
            l1 = list()
            l2 = list()
            l3 = list()
            for j in range(0, self.grid_width):
                s = self.generate_static_object(j, i)
                l1.append(s)
                l2.append(s)
                l3.append(None)
            self.world_map.append(l1)
            self.commonLandData.append(l2)
            self.active_map.append(l3)

        #print vars(self.commonLandData[0][0])
        self.redraw()

    def update_from_source(self, pos, custom_image=None):
        tmp = self.get_block(pos[1], pos[0])
        if isinstance(tmp, GameUI.ActiveTile.ActiveTile):
            # we need to refresh active map!
            #print "array position to update:(%d, %d), replacing % s with: %s" % (pos[0], pos[1], self.active_map[pos[1]][pos[0]], None)
            self.active_map[pos[1]][pos[0]] = None
            return
        # std branch, shouldn't be called anymore!
        # backdoor just to be sure!
        print "!! WARNING!! You shouldn't receive this! replacing % s with: %s" % (
            self.world_map[pos[1]][pos[0]], self.commonLandData[pos[1]][pos[0]])
        self.world_map[pos[1]][pos[0]] = self.commonLandData[pos[1]][pos[0]]

        if not custom_image is None:
            val = self.world_map[pos[1]][pos[0]]
            #custom_image.set_alpha(127)
            val.update_source(custom_image)
            #print vars(val)

    def redraw(self, clearing=None, end_turn=False):
        if not clearing is None:
            self.need_to_redraw = True

        #print self.world_map[0][0]
        if self.image is None:
            self.image = pygame.Surface((self.tile_width * self.grid_width, self.tile_width * self.grid_height))
            self.screen = pygame.display.get_surface()

        self.active_panel = pygame.Surface((self.tile_width * self.grid_width,
                                            self.tile_width * self.grid_height), flags=pygame.SRCALPHA)
        high_priority = list()
        #duplicate code for active_map
        for x in self.active_map:
            for obj in x:
                if isinstance(obj, ActiveTile.ActiveTile) and not obj.hidden:
                    if not clearing is None:
                        obj.set_highlighted("none")
                    if isinstance(obj, GameUI.Unit.Unit):
                        obj.redraw()
                        high_priority.append(obj)
                    elif not isinstance(obj, GameUI.Placeholder.Placeholder):
                        self.active_panel.blit(obj.image, obj.get_rect())

        if self.must_redraw:
            self.active_panel.blit(self.must_redraw.image, self.must_redraw.get_rect())
        for x in high_priority:
            self.active_panel.blit(x.image, x.get_rect())

        if self.need_to_redraw:
            #print "YO, redrawing..."
            self.redraw_world_itself(self.image, clearing, end_turn)
        #self.image.blit(panel, (0, 0))
        self.screen.blit(self.image, self.world_position)
        self.screen.blit(self.active_panel, self.world_position)
        #self.draw_active_data(GI.all_active_data)
        #if not self.must_redraw is None:
        #    self.image.blit(self.must_redraw.image, self.must_redraw.get_rect())

    def redraw_world_itself(self, surf, clearing, end_turn):
        for x in self.world_map:
            #print x
            for obj in x:
                #print vars(obj)
                if obj.skull_time > 0 and end_turn:
                    obj.skull_time -= 1
                    #print "decreasing, now left %s" % obj.skull_time
                if not clearing is None:
                    obj.set_highlighted("none")
                surf.blit(obj.image, obj.get_rect())
        self.need_to_redraw = False

    def draw_active_data(self, data_arr):
        #print "rendering active objects for player %d..." % GI.active_player
        self.userActiveData = data_arr
        unit_arr = list()

        for obj in data_arr:
            #print obj
            #if isinstance(obj, GameUI.Town.Town):
            #    #print obj, obj.unit_inside
            if isinstance(obj, GameUI.Door.Door) and obj.crashed is True:
                obj.walkable = True

            if obj.player_index == GI.active_player:
                obj.set_friendly(2)
                obj.update_source()
                if isinstance(obj, GameUI.Unit.Unit) and not obj.hidden:
                    unit_arr.append(obj)
                    obj.redraw()
                if isinstance(obj, GameUI.Town.Town) and not obj.unit_inside is None:
                    unit_arr.append(obj)
                if isinstance(obj, GameUI.Door.Door):
                    obj.walkable = True

            if obj.player_index != GI.active_player and obj.player_index != -1:
                obj.set_friendly(0)
                if isinstance(obj, GameUI.Door.Door) and obj.crashed is False:
                    obj.walkable = False

            #if obj.hidden:
            #    #print "hidden object: %s" % obj

            if not obj.hidden:
                x, y = obj.position
                self.active_map[y][x] = obj
                if isinstance(obj, GameUI.Town.Town) and not obj.copy or isinstance(obj, GameUI.Castle.Castle):
                    self.update_placeholders(x, y, obj)

            if isinstance(obj, GameUI.Castle.Castle) and obj.player_index == GI.active_player:
                #print "set main castle, it is %s!" % obj
                GI.main_castle = obj
                #print "units inside: %s" % GI.main_castle.units_inside.get_units()

                #self.active_panel.blit(obj.image, obj.get_rect())

        self.need_to_redraw = True

        GI.unitGrid.redraw(unit_arr)

    def update_placeholders(self, x, y, obj):
        if not obj is None:
            blk = self.get_block(y, x + 1)
            place_holder = GameUI.Placeholder.Placeholder((x + 1, y), obj)
            place_holder.image.blit(blk.image, (0, 0))
            self.active_map[y][x + 1] = place_holder
            place_holder = GameUI.Placeholder.Placeholder((x, y + 1), obj)
            place_holder.image.blit(blk.image, (0, 0))
            self.active_map[y + 1][x] = place_holder
            place_holder = GameUI.Placeholder.Placeholder((x + 1, y + 1), obj)
            place_holder.image.blit(blk.image, (0, 0))
            self.active_map[y + 1][x + 1] = place_holder
        else:
            obj = self.generate_static_object(x + 1, y)
            self.world_map[y][x + 1] = obj
            self.update_from_source((x + 1, y))
            obj = self.generate_static_object(x, y + 1)
            self.world_map[y + 1][x] = obj
            self.update_from_source((x, y + 1))
            obj = self.generate_static_object(x + 1, y + 1)
            self.world_map[y + 1][x + 1] = obj
            self.update_from_source((x + 1, y + 1))

    def update_position(self):
        x, y = self.world_position
        self.world_position = (x + self.world_speed[0], y + self.world_speed[1])

    def process_click(self, event):
        pos = event.pos
        m_x = (-self.world_position[0] + pos[0]) / 32
        m_y = (-self.world_position[1] + pos[1]) / 32
        ret = self.get_block(m_y, m_x)

        if event.button == 1:
            if isinstance(ret, GameUI.Unit.Unit) and ret.player_index == GI.active_player:
                GI.window_manager.show_unit_panel(ret)
                GI.selected_unit = ret
                GI.game_core.calc_all_areas()
                return

            if isinstance(ret, GameUI.Placeholder.Placeholder):
                ret = ret.link_to_obj

            if isinstance(ret, GameUI.Castle.Castle) and ret.player_index == GI.active_player and not GI.selected_unit:
                ret.update_info()
                GI.window_manager.show_castle_panel()
                return

            if isinstance(ret, GameUI.Town.Town) and not GI.selected_unit:
                ret.update_info()
                GI.window_manager.show_town_panel(ret)
                return

            #print m_y, m_x
            if not ret is None:
                #print ret.name
                if not GI.game_core.move_to_block((m_x, m_y)):
                    GI.selected_unit = None
                    self.redraw(True)

        if event.button == 3:
            #GI.game_core.center_camera((m_y, m_x))
            if not ret is None:
                ret.update_info()
                if isinstance(ret, GameUI.Unit.Unit):
                    print ret.walk_src
                if isinstance(ret, GameUI.Placeholder.Placeholder):
                    ret = ret.link_to_obj
                if isinstance(ret, GameUI.Castle.Castle) and ret.player_index == GI.active_player:
                    GI.window_manager.show_castle_panel()
                    return
                GI.window_manager.show(ret.get_info())

    def get_block(self, posx, posy):
        if 0 <= posx < self.grid_height and 0 <= posy < self.grid_width:
            # we're within the world grid
            if not self.active_map[posx][posy] is None:
                return self.active_map[posx][posy]
            return self.world_map[posx][posy]
        else:
            return None

    def process_event(self, evt):

        if evt.type == pygame.MOUSEBUTTONUP:
            self.process_click(evt)
            return

        if evt.type == pygame.KEYDOWN:
            if evt.key == pygame.K_DOWN:
                self.world_speed[1] -= 10
            if evt.key == pygame.K_UP:
                self.world_speed[1] += 10
            if evt.key == pygame.K_LEFT:
                self.world_speed[0] += 10
            if evt.key == pygame.K_RIGHT:
                self.world_speed[0] -= 10

        if evt.type == pygame.KEYUP:
            if evt.key == pygame.K_DOWN:
                self.world_speed[1] = 0
            if evt.key == pygame.K_UP:
                self.world_speed[1] = 0
            if evt.key == pygame.K_LEFT:
                self.world_speed[0] = 0
            if evt.key == pygame.K_RIGHT:
                self.world_speed[0] = 0

        if evt.type == pygame.MOUSEMOTION:
            if evt.pos[1] < 10:
                self.world_speed[1] += 10
            if evt.pos[1] > 470:
                self.world_speed[1] -= 10
            if evt.pos[0] < 10:
                self.world_speed[0] += 10
            if evt.pos[0] > 630:
                self.world_speed[0] -= 10
            if 10 < evt.pos[0] < 630:
                self.world_speed[0] = 0
            if 10 < evt.pos[1] < 470:
                self.world_speed[1] = 0

        self.update_position()
