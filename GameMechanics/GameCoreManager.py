__author__ = 'dark-wizard'

import pygame
import GameUI
from GameUI.Missile import Missile
from GameMechanics.GameInfo import GameInfo as GI
from GameMechanics.ButtonWindowManager import ButtonWindowManager as BWM
from GameMechanics.GameSound import load_sound
from GameMechanics.GameSound import play
import random


class GameCoreManager():
    ANIMATION_LENGTH = 100
    backup = None

    total_players = 0
    grid_size = 0
    stop_searching_way = False

    ani_state = 0                           # we move half a tile in one half of second, this var indicates state
    ani_ttr = ANIMATION_LENGTH              # time to refresh
    ani_max_ttr = ANIMATION_LENGTH          # max time before refreshing
    points = list()                         # crucial points of way
    directions = list()                     # directions between crucial points
    ani_pp = 0                              # pointer to current point of animation
    dist = 0
    old_position = (0, 0)

    func_stack = None
    param_stack = None

    def __init__(self, num_of_players, grid_size):
        self.total_players = num_of_players
        self.grid_size = grid_size
        self.battle_sound = load_sound("sword")
        self.fanfare_sound = load_sound("fanfare")

    def center_camera(self, pos, once = False):
        if not GI.ai.working and not once:
            return
        sizex, sizey = pygame.display.get_surface().get_size()
        sizex /= 2
        sizey /= 2
        #print sizex, sizey
        resx = sizex - pos[0] * 32
        resy = sizey - pos[1] * 32

        #print "move camera to (%d, %d)" % (resx, resy)
        GI.worldGrid.world_position = (resx, resy)

    # deprecated
    def get_render_data(self):
        return GI.all_active_data

#=============================================
    def calc_all_areas(self):
        GI.worldGrid.redraw(clearing=True)
        if not self.stop_searching_way:
            GI.game_core.calc_move_area()
            GI.game_core.calc_fight_area()
        else:
            self.stop_searching_way = False
            #print "flag reset"
        GI.worldGrid.need_to_redraw = True

    def calc_move_area(self):
        self.breadth_fast_search(GI.selected_unit.movement, "walk")

    def calc_fight_area(self):
        self.breadth_fast_search(GI.selected_unit.attack_range, "fight")

    def move_obj(self, func=None, params=None):
        if not func is None:
            self.func_stack = func
            self.param_stack = params

        #print "functions are: %s" % str(func)
        GI.window_manager.show_transparent_layer()
        self.ani_ttr += GI.time_passed
        #print self.ani_ttr
        if self.ani_ttr >= self.ani_max_ttr:
            #print "time to update position!"
            self.ani_ttr = 0
            try:
                px, py = self.points[self.ani_pp]
                tx, ty = self.points[self.ani_pp + 1]
                dx, dy = px - tx, py - ty
                obj = GI.selected_unit
            except: 
                return 
            if dx == 0 and dy == 0 or self.ani_pp == len(self.points):
                # we're at finish, stop moving
                #GI.selected_unit.position = (tx, ty)
                self.stop_animation()
                return

            direct = self.directions[self.ani_pp]
            obj.play_walk_animation(direct)
            obj.change_frames(True)
            obj.redraw()
            
            if self.ani_state == 0:
                #we just begin moving
                px, py = px * 32 - dx * 16, py * 32 - dy * 16
                obj.set_absolute_rect(pygame.Rect((px, py), (32, 32)))
                #code for setting object move animation
                self.ani_state = 1
                return
            if self.ani_state == 1:
                px, py = tx * 32, ty * 32
                obj.set_absolute_rect(pygame.Rect((px, py), (32, 32)))
                #code for setting object move animation
                self.ani_state = 0
                self.ani_pp += 1
                #GI.game_core.center_camera((tx, ty))
                #GI.worldGrid.update_from_source(GI.selected_unit.position)

    def get_crucial_points(self, target_pos):
        self.points = list()
        self.directions = list()

        #print "calculating..."
        #print "target position: %s" % str(target_pos)
        cpx, cpy = GI.selected_unit.position
        epx, epy = target_pos
        self.old_position = (cpx, cpy)

        tx, ty = cpx, cpy
        dx = [0, 0, 1, -1]
        dy = [1, -1, 0, 0]

        self.points.append((cpx, cpy))
        # we may just use variable not to choose direction we used before
        while tx != epx or ty != epy:
            actual_distance = self.calc_distance(target_pos, False, (tx, ty))
            for l in range(4):

                tmp_distance = self.calc_distance(target_pos, False, (tx + dx[l], ty + dy[l]))
                if tmp_distance < actual_distance:

                    self.points.append((tx + dx[l], ty + dy[l]))
                    tx, ty = tx + dx[l], ty + dy[l]

                    nm = 0
                    if (dx[l], dy[l]) == (0, 1):
                        nm = GameUI.Unit.Unit.DOWN
                    if (dx[l], dy[l]) == (0, -1):
                        nm = GameUI.Unit.Unit.UP
                    if (dx[l], dy[l]) == (1, 0):
                        nm = GameUI.Unit.Unit.RIGHT
                    if (dx[l], dy[l]) == (-1, 0):
                        nm = GameUI.Unit.Unit.LEFT
                    self.directions.append(nm)
                    break

        tmp = self.points[-1:]
        self.points.append(tmp[0])
        #print "crucial points are: %s" % self.points
        #print "directions are: %s" % self.directions

#standard path-way finder, simple, because the game is simple

    def calc_distance(self, target_pos, verbose=True, from_point=None):
        if from_point is None:
            cpx, cpy = GI.selected_unit.position
        else:
            cpx, cpy = from_point
        epx, epy = target_pos
        dist = abs(cpx - epx) + abs(cpy - epy)
        if verbose:
            print "current pos is: ", GI.selected_unit.position
            print "new pos is:", target_pos
            print "dist is: (%d-%d) + (%d-%d): %d" % (cpx, epx, cpy, epy, dist)
        return dist

    def check_block_highlighting(self, res, hl_type, AI_dfs=False):
        #if not res is None and res.walkable and (not res.walk_highlighted and hl_type == "walk"
        #                                                 or not res.fight_highlighted and hl_type == "fight"
        #                                                 or hl_type == "none")
        if res is None:
            return False
        if res.walkable is False:
            return False
        if res.walk_highlighted and hl_type == "walk":
            return False
        if res.fight_highlighted and hl_type == "fight":
            return False
        if isinstance(res, GameUI.ActiveTile.ActiveTile):
            if isinstance(res, GameUI.Placeholder.Placeholder):
                res.link_to_obj.set_highlighted(hl_type)
                return True
            if AI_dfs:
                return False
            if not AI_dfs:
                #print "Found an active tile, ", res
                res.set_highlighted(hl_type)
        return True

    def breadth_fast_search(self, dist, hl_type, attack_when_found=False):
        if GI.selected_unit is None:
            return
        #print "================================bfs======================"
        tx, ty = tile = GI.selected_unit.position
        res_turn = None
        queue = list()
        turn_list = list()
        queue.append(tile)
        turn_list.append(0)

        turns = 0
        max_turns = dist

        start_block = GI.worldGrid.get_block(ty, tx)
        #print "starting bfs from %s" % start_block
        start_block.set_highlighted(hl_type)
        dx = [0, 0, -1, 1]
        dy = [1, -1, 0, 0]

        while len(queue) > 0:
            
            num = turn_list[0]
            if num >= max_turns:
                break
            elem = queue[0]

            queue = queue[1:]
            turn_list = turn_list[1:]
            for l in range(4):
                res = GI.worldGrid.get_block(elem[1] + dx[l], elem[0] + dy[l])
                if self.check_block_highlighting(res, hl_type) and num < max_turns:
                    #print res.get_info()
                    #mark as highlighted
                    res.set_highlighted(hl_type, not GI.ai.working)
                    queue.append(res.position)
                    turn_list.append(num+1)
            turns += 1
            
            #print "queue: %s\nnums: %s" % (queue, turn_list)

        start_block.set_highlighted("none")
        #GI.worldGrid.redraw()
        #print "---------------------------------------------------------"
        return res_turn
#=============================================

    def move_to_block(self, target_pos):
        target = GI.worldGrid.get_block(target_pos[1], target_pos[0])
        if isinstance(target, GameUI.Placeholder.Placeholder):
            target = target.link_to_obj
        #print "we're applying actions to %s" % target
        #if True:
        #    return

        if target.fight_highlighted and isinstance(target, GameUI.ActiveTile.ActiveTile) and target.is_friendly == 0:
            self.attack_block(target_pos)
            #print "trying to attack", target
            return True

        if not target.walk_highlighted or isinstance(target, GameUI.Unit.Unit):
            return False

        if target.walk_highlighted and isinstance(target, GameUI.Castle.Castle):
            if not target.has_free_space():
                GI.window_manager.show("You can't enter castle, too\n many units there!")
                return True
            self.ani_max_ttr = 100
            target = self.get_nearest_placeholder(target.position)
            #print "target is %s" % target
            target_pos = target.position
            self.get_crucial_points(target_pos)
            GI.worldGrid.redraw(clearing="True")
            self.move_obj([self.enter_castle])
            return True

        if target.walk_highlighted and isinstance(target, GameUI.Town.Town):
            if not target.unit_inside is None:
                GI.window_manager.show("You can't enter town, while\n there's somebody!")
                return True
            self.ani_max_ttr = 100
            if self.get_nearest_placeholder(target_pos) is None:
                return True
            target_pos = self.get_nearest_placeholder(target_pos).position
            self.get_crucial_points(target_pos)
            GI.worldGrid.redraw(clearing="True")
            self.move_obj([self.claim_town], [target_pos])
            return True

        #print target.get_info()
        self.get_crucial_points(target_pos)

        #tx, ty = GI.selected_unit.position
        #old = GI.worldGrid.get_block(ty, tx)
        #print "<old block is % s>" % old
        #GI.worldGrid.update_from_source(old.position)
        #old = GI.worldGrid.get_block(ty, tx)
        #GI.worldGrid.must_redraw = old
        #GI.worldGrid.image.blit(old.image, old.get_rect())
        #print "there's %s after update!" % old
        #old.hidden = True
        GI.worldGrid.redraw(clearing="True")
        #GI.selected_unit.position = target_pos
        self.move_obj()
        #dist = self.breadth_fast_search(GI.selected_unit.movement + 1, "none", target_pos)
        #print "BFS dist is %d, calculated dist is %d" % (dist, self.calc_distance(target_pos))
        return True

    def get_nearest_placeholder(self, target_position):
        dx = [1, -1, 0, 0]
        dy = [0, 0, 1, -1]
        px, py = target_position
        blk = GI.worldGrid.get_block(py, px)
        if isinstance(blk, GameUI.Placeholder.Placeholder):
            return blk

        for l in range(4):
            tx, ty = px + dx[l], py + dy[l]
            blk = GI.worldGrid.get_block(ty, tx)
            if isinstance(blk, GameUI.Placeholder.Placeholder):
                return blk

        return None

    def stop_animation(self):
        #print "functions are: %s" % str(self.func_stack)
        #GI.selected_unit.stop_walk_animation()
        GI.worldGrid.must_redraw = None
        GI.worldGrid.update_from_source(GI.selected_unit.position)
        px, py = GI.selected_unit.position
        #print "now on player position is %s" % GI.worldGrid.get_block(py, px)
        GI.window_manager.hide_transparent_layer()
        #stop object walking animation
        GI.selected_unit.position = (self.points[-1:][0])
        GI.selected_unit.stop_walk_animation()
        self.dist = len(self.points) - 2
        self.points = list()
        self.directions = list()
        self.ani_pp = 0
        self.ani_ttr = self.ANIMATION_LENGTH
        self.ani_max_ttr = self.ANIMATION_LENGTH
        #print "finished!"

        #print "travelled dist is", self.dist
        #print "distance moved: ", self.dist
        GI.selected_unit.movement -= self.dist
        #GI.selected_unit.attack_range -= self.dist

        #time for some magic
        k = 0
        if not self.func_stack is None:
            #print "applying functions..."
            for x in self.func_stack:
                #print "calling %s..." % x
                if not self.param_stack is None and len(self.param_stack) > k:
                    x(self.param_stack[k])
                else:
                    x()
                k += 1
            self.func_stack = None
            self.param_stack = None

        if not GI.selected_unit.hidden:
            self.calc_all_areas()
        GI.worldGrid.draw_active_data(GI.all_active_data)
        if GI.ai.working:
            GI.ai.load_next_unit()

#=============================================
    def remove_from_active_list(self, blk):
        if blk in GI.all_active_data:
            GI.all_active_data.remove(blk)

    def attack_block(self, target_pos):

        target = GI.worldGrid.get_block(target_pos[1], target_pos[0])

        if not isinstance(target, GameUI.ActiveTile.ActiveTile):
            #print "wow, you're suddenly attacking Tile! o_O"
            return False

        if target.is_friendly in [1, 2]:
            return False
        
        if GI.selected_unit.attack_range <= 0:
            return False

        if isinstance(target, GameUI.Placeholder.Placeholder):
            target = target.link_to_obj
        
        if isinstance(GI.selected_unit, GameUI.Archer.Archer) and not GI.ai.working:
            missile = Missile("arrow",GI.selected_unit.get_rect(), target_pos, GI.worldGrid.world_position)
            missile.show_animation()
            
        elif isinstance(GI.selected_unit, GameUI.Wizard.Wizard) and not GI.ai.working:
            missile = Missile("blast",GI.selected_unit.get_rect(), target_pos, GI.worldGrid.world_position)
            missile.show_animation()
          
        elif not GI.ai.working:
            play(self.battle_sound, True)
        
        if isinstance(target, GameUI.Unit.Unit):
            #print "attacking!"
            target.damage(GI.selected_unit.attack - target.defense)
            if target.actual_health <= 0:
                GI.worldGrid.update_from_source(target.position)
                if GI.ai.working:
                    GI.selected_unit.level_up(5)
                else:
                    GI.selected_unit.level_up()
                tpx, tpy = target.position
                blk = GI.worldGrid.get_block(tpy, tpx)
                blk.set_highlighted("skull")
                GI.worldGrid.need_to_redraw = True

        if isinstance(target, GameUI.Castle.Castle) and not target.crashed:
            #print "attacking!"
            target.damage(GI.selected_unit.attack * 5)
            if target.toughness <= 0:
                target.set_crashed(True)
                GI.worldGrid.update_from_source(target.position)
                px, py = target.position
                GI.worldGrid.update_placeholders(px, py, None)
                #print "units inside: %s" % str(target.get_units())

                for r in target.get_units(False):
                    if isinstance(r, GameUI.King.King):
                        #print "leaving King from castle!"
                        r.hidden = False
                        r.actual_health = r.health / 2
                        r.position = target.position

                #print "castle of player #%d destroyed!" % target.player_index
                GI.worldGrid.redraw(clearing=True)
                GI.worldGrid.draw_active_data(GI.all_active_data)

        if isinstance(target, GameUI.Town.Town):
            play(self.fanfare_sound, True)
            #print "attacking town!"
            target.mod_loyalty(-GI.selected_unit.attack * 1.5)
            if target.loyalty <= 0:
                #just notifying
                pl_num = GI.active_player + 1
                if pl_num >= self.total_players:
                    pl_num = 0
                user_data = GI.player_private_data[pl_num]
                old_txt = ""
                if "message" in user_data:
                    old_txt = user_data["message"]
                val = {"message": old_txt + "One of your towns was lost!\n"}
                user_data.update(val)

                # and now updating!
                target.loyalty = 70
                target.set_friendly(2)
                target.unit_inside = None
                target.player_index = GI.active_player
                GI.worldGrid.redraw(clearing=True)

        GI.worldGrid.draw_active_data(GI.all_active_data)
        GI.selected_unit.attack_range -= 1
        #GI.selected_unit.movement -= 1

        self.calc_all_areas()
        #GI.worldGrid.redraw()
        return True

#=============================================
    def get_claim_status(self):
        user_data = GI.player_private_data[GI.active_player]
        #print user_data
        if "claim_days" in user_data:
            days_to_claim = 3 - (GI.turn_number - user_data["claim_days"]) / self.total_players
            target = user_data["claiming_town"]

            if days_to_claim == 0:
                #set town as claimed
                GI.window_manager.show("Town is claimed!")
                target.set_friendly(2)
                target.player_index = GI.active_player
                target.loyalty = 100
                #target.unit_inside = None
                del user_data["claim_days"]
                del user_data["claiming_town"]

                GI.unitGrid.add_unit(target)
                GI.worldGrid.draw_active_data(GI.all_active_data)
            else:
                GI.window_manager.show("You need %d more days to claim\n the town!" % days_to_claim)

#=============================================
# town functions
    def claim_town(self, target_pos):
        #print "entered the town!"
        target = GI.worldGrid.get_block(target_pos[1], target_pos[0])       # - is Town, 100%
        if isinstance(target, GameUI.Placeholder.Placeholder):
            target = target.link_to_obj

        if not isinstance(GI.selected_unit, GameUI.Thief.Thief) and target.is_friendly == 1:
            GI.window_manager.show("You must be a scout to claim!")
            return

        if target.is_friendly == 1:
            # we need to enter before we start claiming
            GI.window_manager.show("Claiming started. \nYou'll lose control on your\n Scout temporarily.")
            self.enter_town(target_pos)
            #GI.worldGrid.redraw(clearing="True")
            tmp = {"claim_days": GI.turn_number, "claiming_town": target}
            GI.player_private_data[GI.active_player].update(tmp)

        if target.is_friendly == 2:
            GI.selected_town = target
            if GI.selected_town.unit_inside is None:
                GI.window_manager.set_leave_disabled(True)
                GI.window_manager.set_enter_disabled(False)

            GI.window_manager.show_right_panel()
        #show menu in the right
        #six rows: 5 soldiers and button "enter city/leave city"
        #if there's somebody, add city to units

    def enter_town(self, target_pos=None):
        if not target_pos is None:
            target = GI.worldGrid.get_block(target_pos[1], target_pos[0])
        else:
            target = GI.selected_town

        if isinstance(target, GameUI.Placeholder.Placeholder):
            target = target.link_to_obj

        #if target is None:
        #    return

        #remove from unit grid
        target.unit_inside = GI.selected_unit
        #target.walkable = False
        GI.unitGrid.remove_unit(GI.selected_unit)
        GI.selected_unit.hidden = True

        GI.worldGrid.redraw(clearing=True)
        GI.worldGrid.draw_active_data(GI.all_active_data)
        GI.worldGrid.update_from_source(GI.selected_unit.position)
        #if GI.selected_unit.movement > 0:
        #    self.stop_searching_way = True

        GI.window_manager.set_leave_disabled(False)
        GI.window_manager.set_enter_disabled(True)
        GI.window_manager.hide_right_panel()

    def leave_town(self, target_pos=None):
        target = GI.selected_town
        #if target is None:
        #    return
        GI.unitGrid.remove_unit(target)
        #GI.unitGrid.add_unit(target.unit_inside)
        GI.selected_unit = target.unit_inside
        GI.selected_unit.hidden = False
        target.unit_inside = None
        GI.worldGrid.draw_active_data(GI.all_active_data)

        GI.window_manager.set_leave_disabled(True)
        GI.window_manager.set_enter_disabled(False)
        GI.window_manager.hide_right_panel()

    def recruit(self, name, target_pos=None):
        if GI.selected_town is None:
            return False
        
        if GI.selected_town.can_recruit is False:
            GI.window_manager.show("You can't recruit more than once a day!")
            return False

        GI.selected_town.can_recruit = False
        GI.selected_town.mod_loyalty(-10)
        if not GI.selected_town.unit_inside is None:
            GI.selected_town.mod_loyalty(5)
        dx = [0, 0, -1, 1]
        dy = [1, -1, 0, 0]
        if target_pos is None:
            target_pos = GI.selected_town.position
        px, py = target_pos

        for l in range(4):
            blk = GI.worldGrid.get_block(py + dy[l], px + dx[l])
            if not blk is None and blk.walkable and (
                    not isinstance(blk, GameUI.ActiveTile.ActiveTile) or isinstance(blk, GameUI.Placeholder.Placeholder)
            ):
                #print "Creating %s in position %s" % (name, blk.position)
                self.add_unit(blk.position, name, GI.active_player)
                GI.worldGrid.draw_active_data(GI.all_active_data)
                break

        GI.window_manager.hide_right_panel()
        return True

#=========================================================================
# castle functions, similar to town
    def enter_castle(self):
        #print "adding %s to %s" % (GI.selected_unit, GI.main_castle)
        target = GI.main_castle
        #remove from unit grid
        target.add_unit_to_castle(GI.selected_unit)
        #target.walkable = False
        GI.unitGrid.remove_unit(GI.selected_unit)
        GI.selected_unit.hidden = True

        GI.worldGrid.redraw(clearing=True)
        GI.worldGrid.draw_active_data(GI.all_active_data)
        GI.worldGrid.update_from_source(GI.selected_unit.position)
        #if GI.selected_unit.movement > 0:
        #    self.stop_searching_way = True
        GI.window_manager.show_castle_panel()

    def leave_castle(self):
        """don't forget to set GI.selected unit, when clicking menu"""
        target = GI.main_castle
        #print "leaving from %s" % target
        target.remove_unit_from_castle(GI.selected_unit)
        GI.unitGrid.add_unit(GI.selected_unit)
        GI.selected_unit.hidden = False
        #print "leaving to %s" % str(GI.selected_unit.position)
        #GI.selected_unit.position = GI.main_castle.position
        GI.worldGrid.draw_active_data(GI.all_active_data)

        GI.window_manager.hide_right_panel()

#=============================================
    def get_nearest_active_cells(self, pos, offset=1, only_enemy=False):
        res = list()
        dx = [0, 0, -1, 1]
        dy = [1, -1, 0, 0]
        for l in range(4):
            blk = GI.worldGrid.get_block(pos[1] + dy[l] * offset, pos[0] + dx[l] * offset)
            if isinstance(blk, GameUI.Unit.Unit):
                if not only_enemy or blk.player_index != GI.active_player:
                    res.append(blk)
        return res

    def restore_from_backup(self):
        #GI.worldGrid.redraw(clearing=True)
        GI.all_active_data = list()
        for x in self.backup:
            GI.all_active_data.append(x)
        GI.worldGrid.draw_active_data(GI.all_active_data)
        GI.window_manager.show("Data restored!")

    def create_backup(self):
        #print "creating backup..."
        self.backup = list()
        for x in GI.all_active_data:
            res = x.__class__(x.position)
            #print res
            res.__dict__.update(x.__dict__)
            #type(x)(x.position)
            self.backup.append(res)

    def change_turn(self):
        #creating backup
        self.create_backup()

        # auto attack
        for x in GI.main_castle.units_inside.get_units():
            if isinstance(x, GameUI.Archer.Archer) or isinstance(x, GameUI.Wizard.Wizard):
                #distant attack
                dist = x.attack_range
                #print "selecting %s with %s attack range" % (x, dist)
                for l in reversed(range(1, dist + 1)):
                    #print "choosing %s dist..." % l
                    cells = self.get_nearest_active_cells(x.position, l, only_enemy=True)
                    #print "enemies are: %s" % cells
                    if len(cells) > 0:
                        #print "attacking %s..." % cells
                        y = cells[0]
                        y.damage(x.attack)
                        if y.actual_health <= 0:
                            GI.worldGrid.update_from_source(y.position)
                            x.level_up()
                            tpx, tpy = y.position
                            blk = GI.worldGrid.get_block(tpy, tpx)
                            blk.set_highlighted("skull")

        GI.selected_unit = None
        GI.selected_town = None
        GI.window_manager.reset_turn = False

        GI.worldGrid.redraw(clearing=True, end_turn=True)
        my_towns = 0
        enemy_towns = 0

        for obj in GI.all_active_data:
            #checking lose conditions - if king is dead or all towns are captured
            if isinstance(obj, GameUI.King.King):
                if obj.actual_health <= 0:
                    GI.window_manager.show("Player #%d has lost!" % (obj.player_index + 1), False)
                    return

            if obj.player_index == GI.active_player:
                obj.set_friendly(0)
                obj.update_source()

                if isinstance(obj, GameUI.Unit.Unit):
                    ex = obj.__class__((-1, -1))
                    obj.attack_range = ex.attack_range
                    obj.movement = ex.movement
                if isinstance(obj, GameUI.Town.Town):
                    obj.can_recruit = True

                    if obj.loyalty <= 0:
                        self.convert_town(obj, 2, 70)
                    else:
                        obj.mod_loyalty(2)
                        if not obj.unit_inside is None:
                            obj.mod_loyalty(2)

                        if obj.loyalty <= 50:
                            destiny = random.random()
                            if destiny < 0.5:
                                self.convert_town(obj, 1, 0)

            if isinstance(obj, GameUI.Town.Town):
                if obj.player_index == GI.active_player:
                    my_towns += 1
                elif obj.player_index != -1:
                    enemy_towns += 1

        #print "Total towns for player %d: %d" % (GI.active_player, my_towns)
        #print "Total towns for other player: %d" % enemy_towns

        if my_towns == 0:
            GI.window_manager.show("Player #%d has lost!" % (GI.active_player + 1),False)
            return
        if enemy_towns == 0:
            GI.window_manager.show("Player #%d has won!" % (GI.active_player + 1), False)
            return

        new_player = GI.active_player + 1
        if new_player == self.total_players:
            new_player = 0
        GI.active_player = new_player
        GI.turn_number += 1
        
        GI.worldGrid.draw_active_data(GI.all_active_data)
        if not GI.ai is None and GI.active_player == GI.ai.player_number:
            GI.ai.get_control(GI.all_active_data)
            GI.window_manager.show_transparent_layer()
        else:
            for x in GI.all_active_data:
                if isinstance(x, GameUI.Unit.Unit):
                    x.heal()
            GI.window_manager.show("Player #%d turn!" % (new_player + 1))
            user_data = GI.player_private_data[GI.active_player]
            if "message" in user_data:
                GI.window_manager.show(user_data["message"])
                del user_data["message"]
            self.get_claim_status()
            pos = GI.main_castle.position
            self.center_camera(pos, True)

    def convert_town(self, obj, fraction, loyalty):
        user_data = GI.player_private_data[GI.active_player]
        old_txt = ""
        if "message" in user_data:
            old_txt = user_data["message"]
        val = {"message": old_txt + "One of your towns was lost!\n"}
        user_data.update(val)
        obj.unit_inside = None
        obj.loyalty = loyalty
        obj.set_friendly(fraction)

#=============================================
    def generate_towns(self):
        l = list()
        total = random.randint(4, 7)
        #total = 3

        #row, column = 5, 10
        row, column = 5, random.randint(self.grid_size[0] / 2 - 6, self.grid_size[0] / 2 + 6)
        tile = GameUI.Town.Town((row, column))
        tile.player_index = 0
        tile.loyalty = 100
        tile.copy = False
        l.append(tile)
        #print row, column

        row, column = self.grid_size[0], random.randint(self.grid_size[0] / 2 - 6, self.grid_size[0] / 2 + 6)
        tile = GameUI.Town.Town((row, column))
        tile.player_index = 1
        tile.loyalty = 100
        tile.copy = False
        l.append(tile)
        #print row, column

        dist = self.grid_size[0] - 3
        seed = float(dist) / total
        tmp = 7.0
        for i in range(total):
            px = random.randint(4, self.grid_size[0]-4)
            py = int(tmp)
            tmp += seed
            #print px, py
            tile = GameUI.Town.Town((py, px))
            tile.player_index = -1
            tile.copy = False
            l.append(tile)
            #print px, py

        GI.all_active_data += l

#=============================================
    def add_unit(self, position, class_name, player_index, just_for_fun=False):
        parts = class_name.split('.')
        module = ".".join(parts[:-1])
        cls = __import__(module)
        for comp in parts[1:]:
            cls = getattr(cls, comp)

        elem = cls(position)
        if isinstance(elem, GameUI.Unit.Unit):
            #elem.get_hp_surface()
            self.load_walk_animation(elem)
        elem.player_index = player_index

        if just_for_fun is False:
            GI.all_active_data.append(elem)

        return elem
        #GI.worldGrid.draw_active_data(GI.all_active_data)

    def load_walk_animation(self, elem):
        link_base = elem.base_sprite_name
        #print "loading animation for '%s'" % link_base
        self.lst = list()
        self.lst_name = list()
        path_str = "images/" + link_base + "/"
        for i in range(4):
            for j in range(1, 3):
                name = link_base + "_" + elem.position_names[i] + str(j) + ".gif"
                tmp_img = pygame.image.load(path_str + name).convert_alpha()
                self.lst.append(tmp_img)
                self.lst_name.append(name)
        #        #print name
        #print "frames loaded!"
        #print "names list: %s" % self.lst_name
        elem.load_tiles(self.lst, self.lst_name)

    def new_game(self):
        self.generate_towns()

        for x in range(self.total_players):
            #add king
            pos = [10, 0]
            if x != 0:
                pos[1] = self.grid_size[1] - 1
            tmp = self.add_unit((pos[1], pos[0]), "GameUI.King.King", x)

            #add knight
            pos = [11, 10]
            if x != 0:
                pos[1] = self.grid_size[1] - pos[1]
            tmp = self.add_unit((pos[1], pos[0]), "GameUI.Knight.Knight", x)

            #add wizard
            pos = [8, 8]
            if x != 0:
                pos[1] = self.grid_size[1] - 1
            tmp = self.add_unit((pos[1], pos[0]), "GameUI.Wizard.Wizard", x)
            
            #add archer
            pos = [12, 7]
            if x != 0:
                pos[1] = self.grid_size[1] - 1
            tmp = self.add_unit((pos[1], pos[0]), "GameUI.Archer.Archer", x)

            #add thief
            pos = [8, 1]
            if x != 0:
                pos[1] = self.grid_size[1] - 2
            tmp = self.add_unit((pos[1], pos[0]), "GameUI.Thief.Thief", x)

            #add castle
            pos = [self.grid_size[0] / 2, 1]
            if x != 0:
                pos[1] = self.grid_size[1] - 3
            tmp = GameUI.Castle.Castle((pos[1], pos[0]))
            tmp.player_index = x
            GI.all_active_data.append(tmp)

