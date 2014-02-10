__author__ = 'dark-wizard'
from GameMechanics.GameInfo import GameInfo as GI
from collections import defaultdict
import random
import GameUI
import pygame

### TODO: set working = False after moving objects... - done!
### TODO: think about moving, maybe timer?      - done!
### TODO: squads, attacks and back attacks
### TODO: add aggressive option to AI           - done!


class AIManager:
    all_data = list()
    player_number = 0
    tasks = defaultdict(list)
    stats = {}
    bfs_run = 0
    active_unit_number = 0

    town_list = list()
    town_ptr = 0

    working = False
    need_to_redraw = False
    need_to_switch = False
    prev_action = ""
    cut = False

    current_squad = 0
    num_in_squad = 1
    ready_squads = list()

    dx = [0, 0, -1, 1]
    dy = [1, -1, 0, 0]

    def __init__(self, player_number):
        print "[Loaded AI for player #%d]" % player_number
        self.player_number = player_number

#=========================================================================
#step 0: AI receives control
    def get_control(self, data):
        print "[Start AI work!]"
        self.prev_action = ""
        self.active_unit_number = 0
        self.working = True
        self.all_data = list()
        self.need_to_redraw = True
        for x in data:
            if isinstance(x, GameUI.Town.Town) and x.player_index == GI.active_player and not x in self.town_list:
                self.town_list.append(x)
                #self.town_ptr += 1
            if x.player_index == self.player_number and isinstance(x, GameUI.Unit.Unit):
                self.all_data.append(x)
                if not x in self.stats:
                    self.load_default_stats_and_tasks(x)
        print "[parsed array]"
        print "[all stats for this turn is: %s]" % self.stats
        print "[all tasks for this turn is: %s]" % self.tasks
        print "[towns are: %s]" % self.town_list
        self.get_all_chars()

#=========================================================================
#step 1: AI calculates tasks, if needed
    def get_all_chars(self):
        for x in self.all_data:
            self.cut = False
            print "[processing object %s]" % x
            res = self.check_state(x)
            if res == "error":
                raise Exception("Failed to get data!")
            if res == "hp_decreased":
                print "[somebody attacked this unit!]"
                if len(self.tasks[x]) > 0:
                    print "[just going forward!]"
                else:
                    print "[time for revenge!]"
                    self.attack_nearest_unit(x)
                #if not target is None:
                #    self.add_task(x, "attack", target, 0)
                self.stats[x]["hp"] = x.actual_health
            if res == "empty_task":
                print "[empty task, creating...]"
                self.create_new_task(x)

        self.load_next_unit()

    def load_default_stats_and_tasks(self, x):
        val = self.tasks[x]
        dct = {x: {"hp": x.actual_health}}
        if isinstance(x, GameUI.Knight.Knight) or isinstance(x, GameUI.Wizard.Wizard) or isinstance(x, GameUI.Archer.Archer):
            dct[x].update({"squad": self.current_squad})
        self.stats.update(dct)

        print "[data updated!]"
        print "data is: tasks: %s" % self.tasks
        print "data is: stats: %s" % self.stats

    def check_state(self, x):                  # function to be sure every unit have a task and etc...
        stat = None
        task = self.tasks[x]
        if x in self.stats:
            stat = self.stats[x]

        if stat is None:
            self.load_default_stats_and_tasks(x)
            return "empty_task"

        if not stat is None and x.actual_health < stat["hp"]:
            return "hp_decreased"
        if len(task) <= 0:
            return "empty_task"
        return "ok"

#================================================
    def remove_task(self, obj):
        del self.tasks[obj][0]

    def add_task(self, obj, task_name, task_param, index=None):
        if self.cut:
            print "[can't add task, you cut actions for this unit!]"
            return
        print "[adding %s to tasks]" % task_name
        #slicing actions, if action is "move", just need to verify, if we can still do what we wanted
        if task_name == "move" and len(task_param) > 1:
            print "[cut \"move\" action]"
            task_param = task_param[:1]
            self.cut = True
        task_entry = self.tasks[obj]
        new_task = {task_name: task_param}
        if index is None:
            task_entry.append(new_task)
        else:
            task_entry.insert(index, new_task)
        print "[new task is: %s]" % task_entry
        #self.tasks[obj].append(task_entry)

    def create_new_task(self, x):                  # creating task based on unit class
        #many ifs - rewrite later, just add move option
        size = GI.game_core.grid_size[0]
        print "[random size: %d]" % size
        if isinstance(x, GameUI.King.King):
            #calc logic for king
            print "[castle info: %s]" % GI.main_castle.get_info()
            if GI.main_castle.crashed:          # if the castle is crashed
                print "[time for revenge!]"
                self.attack_nearest_unit(x)

            if GI.main_castle.has_unit(x):       # if King already in castle - just wait
                self.add_task(x, "wait", [])
                return

            if not GI.main_castle.crashed:
                res = self.get_nearest_cell(x, GI.main_castle)
                route = self.extended_bfs(x, res, x.movement)
                if route:
                    self.add_task(x, "move", route)
                    self.add_task(x, "enter", GI.main_castle)
            return

        if isinstance(x, GameUI.Knight.Knight) or isinstance(x, GameUI.Archer.Archer) or isinstance(x, GameUI.Wizard.Wizard):
            # working with warriors
            print "[checking ability to attack somebody!]"
            #enemy = self.get_nearest_enemy(x)
            #nb = self.get_nearest_cell(x, enemy)
            #if not nb is None:
            #    dist = GI.game_core.calc_distance(nb.position, False, x.position)
            #    print "[distance is: %s]" % dist
            #    if dist <= x.movement or self.get_enemy_in_range(x,enemy):
            #        print "[decided to attack instead of moving to town!]"
            self.attack_nearest_unit(x)
            return

            print "[there are no enemies to attack!]"
            print "[trying to attack towns!]"
            sq_num = self.stats[x]["squad"]
            ready = sq_num in self.ready_squads
            if ready:
                print "[our squad #%d is ready to attack!]" % sq_num
                all_towns = list()
                self.get_nearest_town(x, 0, all_towns)
                for dct in all_towns:
                    town = dct["town"]
                    nb = self.get_nearest_cell(x, town)
                    if nb is None:
                        print "[can't attack at this moment, waiting...]"
                        self.add_task(x, "wait", [])
                        return
                    else:
                        print "[preparing to attack town %s!]" % town
                        route = self.extended_bfs(x, nb, x.movement)
                        self.add_task(x, "move", route)
                        self.add_task(x, "attack", town)
                        return
            else:
                print "[we need to wait a bit more, going for patrol now...]"
            print "[selecting town with index #%d]" % self.town_ptr
            tmp = self.town_list[self.town_ptr]
            self.town_ptr += 1
            if self.town_ptr == len(self.town_list):
                self.town_ptr = 0
            res = self.get_nearest_cell(x, tmp)
            dist = GI.game_core.calc_distance(res.position, False, x.position)
            if dist == 0:
                self.add_task(x, "wait", [])
                return
            route = self.extended_bfs(x, res, x.movement)
            if route:
                self.add_task(x, "move", route)
            return

        if isinstance(x, GameUI.Thief.Thief):
            # processing thief
            if not x.hidden:        # thief isn't in town
                all_towns = list()
                self.get_nearest_town(x, 2, all_towns)
                print "[all current players' towns: %s]" % all_towns
                print "[gathering info about towns...]"
                for dct in all_towns:
                    town = dct["town"]
                    if town.unit_inside is None:
                        print "[town found!]"
                        res = self.get_nearest_cell(x, town)
                        if not res is None:
                            route = self.extended_bfs(x, res, x.movement)
                            if route:
                                self.add_task(x, "move", route)
                                self.add_task(x, "enter", town)
                                self.add_task(x, "recruit", "rogue")
                                return
                        else:
                            self.add_task(x, "wait", [])

                # this branch is for claiming
                print "[%s didn't find the place to enter, begin claiming...]" % x
                all_towns = list()
                self.get_nearest_town(x, 1, all_towns)
                print "[all neutral towns: %s]" % all_towns
                print "[gathering info about towns...]"
                for dct in all_towns:
                    town = dct["town"]
                    res = self.get_nearest_cell(x, town)
                    if not res is None and town.unit_inside is None:
                        route = self.extended_bfs(x, res, x.movement)
                        if route:
                            self.add_task(x, "move", route)
                            self.add_task(x, "claim", town)
                            for l in range(3):
                                self.add_task(x, "check", [])
                            self.add_task(x, "recruit", "rogue")
                            return
                self.add_task(x, "wait", [])
                #do smth
            if x.hidden and x.actual_health > 0:        # thief already in town
                #this branch is for recruiting...
                self.add_task(x, "recruit", self.get_unit_for_squad())
            return

        print "[!!! WARNING! old methods! NO MORE RANDOM !!!]"
        print "[generating random cell on map...]"
        blk = None

        while True:
            tx, ty = random.randrange(0, size), random.randrange(0, size)
            blk = GI.worldGrid.get_block(ty, tx)
            print "[trying (%d, %d):(%s)]" % (tx, ty, blk)
            ans = GI.game_core.check_block_highlighting(blk, "walk", True)
            if ans:
                print "[found block!]\n[Searching for direction...]"
                route = self.extended_bfs(x, blk, x.movement)
                if route:
                    self.add_task(x, "move", route)
                    #print "[new task for %s is %s]" % (x, self.tasks[x])
                    #print "[total tasks for %s is: %s]" % (x, len(self.tasks[x]))
                    #print "[=============]"
                    break
                else:
                    print "[that block hadn't lead anywhere :(]"

    def extended_bfs(self, start_block, stop_block, step_size=1):
        way = list()
        queue = list()
        labels = list()
        end_label = 0
        #will mark tiles we walk with global bfs counter, they are unique
        self.bfs_run += 1
        queue.append(start_block)
        labels.append(0)
        start_block.mark = self.bfs_run

        while len(queue) > 0:
            end_block = queue[0]
            cx, cy = end_block.position
            cl = labels[0]
            queue = queue[1:]
            labels = labels[1:]
            #print "[now processing %s, index is: %s]" % (end_block, cl)
            #print "[position: (%d, %d)]" % (cx, cy)
            if end_block == stop_block:
                print "[way found, restoring...]"
                way.append(end_block)
                end_label = cl
                break

            for l in range(0, len(self.dx)):
                blk = GI.worldGrid.get_block(cy + self.dy[l], cx + self.dx[l])
                #print "==============="
                #if not blk is None:
                #    print "block: %s, position: (%d, %d))" % (blk, blk.position[0], blk.position[1])
                #check, if blk is Tile, or Door, and we can mark it
                if GI.game_core.check_block_highlighting(blk, "walk", AI_dfs=True) and blk.mark != self.bfs_run:
                    blk.mark = self.bfs_run
                    blk.label = cl + 1
                    labels.append(cl + 1)
                    queue.append(blk)

        print "[way length: %d]" % end_label
        if end_label == 0:
            return []
        tile = way[0]
        while tile != start_block:
            cx, cy = tile.position
            #print "[position: (%d, %d)]" % (cx, cy)
            for l in range(0, len(self.dx)):
                blk = GI.worldGrid.get_block(cy + self.dy[l], cx + self.dx[l])
                if not blk is None and blk.mark == self.bfs_run and blk.label == end_label - 1:
                    tile = blk
                    end_label -= 1
                    way.append(blk)
                    break

        last_point = way[0].position
        way.reverse()
        res = list()
        for x in way:
            res.append(x.position)

        res = res[::step_size]
        res = res[1:]
        if len(res) == 0 or res[-1:][0] != last_point:
            res.append(last_point)
        print "[way to cell is: %s]" % res
        return res

#================================================
    def attack_nearest_unit(self, x):
        GI.selected_unit = x
        #GI.game_core.breadth_fast_search(x.attack_range, "fight")
        enemy_list = list()
        self.get_nearest_enemy(x, enemy_list)
        print "[all enemies are: %s]" % str(enemy_list)
        if len(enemy_list) == 0:
            print "[no enemies found! :(]"

        for dct in enemy_list:
            enemy = dct["enemy"]
            nb = self.get_nearest_cell(x, enemy)
            if not nb is None:
                route = self.extended_bfs(x, nb, x.movement)
                print "---------%s-----------" %nb
                if route:
                    self.add_task(x, "move", route)
                    self.add_task(x, "attack", enemy)
                    return

        # here we should put function for attacking towns and castles
        self.add_task(x, "wait", [])
        return

    #deprecated
    
    def get_enemy_in_range(self, unit, enemy):
        ux, uy = unit.position
        ex, ey = enemy.position
        urange = unit.attack_range

        if ux + urange == ex  and ey == uy:
            return True
        if ux - urange == ex  and ey == uy:
            return True
        if uy + urange == ey  and ex == ux:
            return True
        if uy - urange == ey  and ex == ux:
            return True
        return False

    def get_nearest_enemy(self, obj, all_enemies_list=None):
        res = 1 << 31
        cell = None

        print "[calculating distances to enemies:]"
        print "[searching enemies...]"
        active = GI.worldGrid.active_map
        for x in active:
            # x is list
            for elem in x:
                if isinstance(elem, GameUI.Unit.Unit) and elem.player_index != self.player_number:
                    dist = GI.game_core.calc_distance(elem.position, False, obj.position)
                    print "[unit found, distance is %d]" % dist
                    if not all_enemies_list is None:
                        dct = {"enemy": elem, "dist": dist}
                        all_enemies_list.append(dct)
                    if dist <= res:
                        res = dist
                        cell = elem

        if not all_enemies_list is None:
            all_enemies_list.sort(key=lambda val: val["dist"])
        print "[dist to nearest is: %d]" % res
        print "[nearest cell is: %s]" % cell
        return cell

    def get_nearest_town(self, obj, only_ownership=1, all_towns_list=None):
        """only ownership: 1 - only neutral, 2 - only friendly, 0 - only enemy"""
        print "[calculating distances to towns:]"
        print "[searching towns...]"
        cell = None
        res = 1 << 31
        active = GI.worldGrid.active_map
        for x in active:
            # x is list
            for elem in x:
                if isinstance(elem, GameUI.Town.Town) and (
                    only_ownership == 1 and elem.player_index == -1
                    or only_ownership == 0 and elem.player_index != GI.active_player and elem.player_index != -1
                    or only_ownership == 2 and elem.player_index == GI.active_player
                ):
                    dist = GI.game_core.calc_distance(elem.position, False, obj.position)
                    if not all_towns_list is None:
                        dct = {"town": elem, "dist": dist}
                        all_towns_list.append(dct)
                    if dist <= res:
                        res = dist
                        cell = elem
                    print "[town found, distance is %d]" % dist
        if not all_towns_list is None:
            all_towns_list.sort(key=lambda town: town["dist"])
        print "\n[dist to nearest town is: %d]" % res
        print "[nearest town is: %s]" % cell
        return cell

    def get_nearest_cell(self, x, target):
        if target is None:
            return None

        dist = 1 << 31
        res = None
        px, py = target.position
        for l in range(len(self.dx)):
            blk_inst = GI.worldGrid.get_block(py + self.dy[l], px + self.dx[l])
            if not blk_inst is None:
                blk_dist = GI.game_core.calc_distance(blk_inst.position, False, x.position)
                print "[checking %s..., distance=%d]" % (blk_inst, blk_dist)
                if blk_dist < dist and (
                        not isinstance(blk_inst, GameUI.ActiveTile.ActiveTile) or isinstance(blk_inst, GameUI.Placeholder.Placeholder)
                ):
                    dist = blk_dist
                    res = blk_inst
        print "\n[dist to nearest cell is: %d]" % dist
        print "[nearest cell is: %s]" % res
        return res

    def get_unit_for_squad(self):
        #squad = list()
        print "[looking for squad #%d]" % self.current_squad
        print "[total units in active squad: %s]" % self.num_in_squad
        #for x in self.all_data:
        #    if x in self.stats and "squad" in self.stats[x] and self.stats[x]["squad"] == self.current_squad:
        #        squad.append(x)
        res = ""
        if self.num_in_squad == 3:
            self.ready_squads.append(self.current_squad)
            self.current_squad += 1
            self.num_in_squad = 1
            return "warrior"
        if self.num_in_squad == 2:
            res = "wizard"
        if self.num_in_squad == 1:
            res = "archer"
        self.num_in_squad += 1
        return res

#=========================================================================
# step 2: AI doing functions
    def do_part_time_jobs(self):
        num = self.active_unit_number - 1
        if num >= 0 and self.prev_action == "move":
            unit = self.all_data[num]
            print "[switching to %s again]" % unit

            task = self.tasks[unit]
            print "[current task is: %s]" % str(task)
            if len(task) > 0 and "attack" in task[0]:
                # adding ability to attack after movement
                target = task[0]["attack"]
                #trying to attack, because we are at the endpoint
                print "[attacking %s %d times]" % (target, unit.attack_range)
                while GI.game_core.attack_block(target.position):
                    self.need_to_redraw = False
                self.need_to_redraw = True
                self.working = True
                self.remove_task(unit)
                return

            if len(task) > 0 and "enter" in task[0] and unit.movement >= 1:
                #adding ability to enter buildings after movement
                target = task[0]["enter"]
                GI.selected_unit = unit
                if isinstance(target, GameUI.Castle.Castle):
                    GI.game_core.enter_castle()
                if isinstance(target, GameUI.Town.Town):
                    GI.game_core.enter_town(target.position)
                self.remove_task(unit)
                return

    def load_next_unit(self):
        self.cut = False
        self.do_part_time_jobs()
        self.need_to_switch = False
        self.do_your_job_lazy_ass()
        self.active_unit_number += 1
   
    def do_work(self, x, plan):
        if "wait" in plan:
            print "[object %s waits for a star from the sky...]" % x
            #just do nothing
            self.remove_task(x)
            self.need_to_switch = True
            return

        if "attack" in plan:
            target = plan["attack"]
            pos = target.position
            print "[trying to attack %s...]" % target
            GI.selected_unit = x
            while x.attack_range > 0:
                GI.game_core.attack_block(pos)
                self.need_to_redraw = False
            self.remove_task(x)
            self.need_to_switch = True
            return

        if "enter" in plan:
            # enter town or castle
            target = plan["enter"]
            print "[entering to %s...]" % target
            GI.selected_unit = x
            if isinstance(target, GameUI.Castle.Castle):
                GI.game_core.enter_castle()
            if isinstance(target, GameUI.Town.Town):
                GI.game_core.enter_town(target.position)
            self.remove_task(x)
            self.need_to_switch = True
            return

        if "move" in plan:
            #here we should move

            target_pos = walk_arr = plan["move"][0]
            target = GI.worldGrid.get_block(target_pos[1], target_pos[0])
            if isinstance(target, GameUI.ActiveTile.ActiveTile) and not isinstance(target, GameUI.Placeholder.Placeholder):
                print "[waiting for ability to move...]"
                self.need_to_switch = True
                return

            #print "[plans to walk: %s]" % walk_arr
            GI.selected_unit = x
            plan["move"] = plan["move"][1:]
            if len(plan["move"]) == 0:
                self.remove_task(x)
                self.prev_action = "move"

            self.need_to_redraw = True
            GI.game_core.center_camera(x.position)
            GI.game_core.get_crucial_points(target_pos)
            GI.game_core.move_obj()
            print "[---]"
            return 

        if "recruit" in plan:
            # recruit new unit
            #target = self.get_unit_for_squad()
            target = plan["recruit"]
            town_to_recruit = self.get_nearest_town(x, 2)
            GI.selected_town = town_to_recruit
            print "[recruiting new unit: %s from %s]" % (target, town_to_recruit)
            if target == "rogue":           # recruiting
                GI.game_core.recruit("GameUI.Thief.Thief", town_to_recruit.position)
            if target == "archer":
                GI.game_core.recruit("GameUI.Archer.Archer", town_to_recruit.position)
            if target == "wizard":
                GI.game_core.recruit("GameUI.Wizard.Wizard", town_to_recruit.position)
            if target == "warrior":
                GI.game_core.recruit("GameUI.Knight.Knight", town_to_recruit.position)

            self.remove_task(x)
            self.need_to_switch = True
            return

        if "claim" in plan:
            target = plan["claim"]
            pos = target.position
            print "[claiming town in position (%d, %d)]" % pos
            GI.selected_unit = x
            GI.game_core.claim_town(pos)
            self.remove_task(x)
            self.need_to_switch = True
            return 

        if "check" in plan:
            print "[checking for claiming...]"
            GI.game_core.get_claim_status()
            self.remove_task(x)
            self.need_to_switch = True

    def do_your_job_lazy_ass(self):
        self.prev_action = ""
        if self.active_unit_number < len(self.all_data):
            num = self.active_unit_number
            unit = self.all_data[num]
            try:
                plan = self.tasks[unit][0]
                self.do_work(unit, plan)
            except:
                self.need_to_switch = True
            return

        self.working = False
        GI.window_manager.hide_transparent_layer()
        GI.game_core.change_turn()

if __name__ == "__main__":
    ai = AIManager(1)
    ai.get_control(GI.all_active_data)
