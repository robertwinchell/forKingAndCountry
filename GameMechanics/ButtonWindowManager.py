__author__ = 'dark-wizard'

#this class is used for cancelling turn or ending it
#also for windows

import pygame
import sys
import UI
from GameMechanics.ColorPalette import ColorPalette as Palette
from GameMechanics.GameInfo import GameInfo as GI
from GameUI.Unit import Unit
from GameUI.Town import Town
from GameMechanics.GameSound import load_sound
from GameMechanics.GameSound import play
from os import system

### TODO: enter castle normally, via map


class ButtonWindowManager():

    yes_sir_sound = None
    trumpet_sound = None

    window_opened = False
    window = None
    image = None
    rect_size = None
    size = None
    end_turn_button = None
    cancel_button = None
    cancelable = True

    skip_rect = None
    cancel_rect = None
    reset_turn = False

    right_panel = None
    right_panel_position = None
    right_panel_state = 0               # 0 - closed, 1 - opening, 2 - opened, 3 - closing
    right_panel_closing = False

    unit_panel = None
    unit_panel_position = (240, 380)

    max_left_position = 0
    max_right_position = 0

    text_buffer = list()
    dirty_flag = False
    screen_buffer = None

    castle_active = False

    #unit_array = ["Knight", "Thief", "", "", ""]
    unit_array = ["GameUI.Knight.Knight", "GameUI.Thief.Thief", "GameUI.Wizard.Wizard", "GameUI.Archer.Archer"]
    enter_button_position = (40, 40 * (len(unit_array) + 1) + 20)
    enter_button = None
    enter_button_disabled = False

    leave_button_position = (40, 40 * (len(unit_array) + 2) + 20)
    leave_button = None
    leave_button_disabled = False

    tl_active = False              # check for transparent layer

    btn_array = list()

    def __init__(self):
        self.size = pygame.display.get_surface().get_size()
        self.window = pygame.Surface(self.size, flags=pygame.SRCALPHA)
        self.rect_size = pygame.Rect((self.size[0] - 300) / 2, (self.size[1] - 200) / 2, 300, 200)
        self.image = self.window.copy()

        self.option_button = UI.Button.Button("Options", 0, 0)
        self.quit_button = UI.Button.Button("Quit Game", 0, 0)
        self.menu_button = UI.Button.Button("Main Menu", 0, 0)
        self.end_turn_button = UI.Button.Button("End Turn", 0, 0)
        self.cancel_button = UI.Button.Button("Cancel Turn", 0, 0)
        
        cancel_up_left = (0, self.size[1] - self.cancel_button.get_height())
        skip_up_left = (0, self.size[1] - self.cancel_button.get_height() - self.end_turn_button.get_height() - 2)
        quit_up_left = (0, self.size[1] - self.end_turn_button.get_height() - self.cancel_button.get_height() - self.quit_button.get_height() - 4)
        menu_up_left = (0, self.size[1] - self.end_turn_button.get_height() - self.cancel_button.get_height() - self.quit_button.get_height() - self.menu_button.get_height() - 6)
        #option_up_left = (0, self.size[1] - self.end_turn_button.get_height() - self.cancel_button.get_height() - self.quit_button.get_height() - self.menu_button.get_height() - self.menu_button.get_height() - 8)

        self.image.blit(self.cancel_button.image, cancel_up_left)
        self.image.blit(self.end_turn_button.image, skip_up_left)
        self.image.blit(self.quit_button.image, quit_up_left)
        self.image.blit(self.menu_button.image, menu_up_left)
        self.image.blit(self.option_button.image, menu_up_left)
        
        self.quit_rect = pygame.Rect(quit_up_left, self.quit_button.get_size())        
        self.skip_rect = pygame.Rect(skip_up_left, self.end_turn_button.get_size())
        self.cancel_rect = pygame.Rect(cancel_up_left, self.cancel_button.get_size())
        self.menu_rect = pygame.Rect(menu_up_left, self.menu_button.get_size())
        #self.option_rect = pygame.Rect(option_up_left, self.option_button.get_size())

        self.redraw_right_panel()
        self.back_to_main_rect = pygame.Rect(0,0,0,0)

        self.yes_sir_sound = load_sound("yes_sir")
        self.trumpet_sound = load_sound("trumpet")
        #print self.rect_size

    def redraw(self):
        tmp = pygame.Surface(self.size, flags=pygame.SRCALPHA)
        self.image = tmp.copy()
        if self.dirty_flag and self.window_opened:
            self.draw_buffer()

        self.image.blit(self.window, (0, 0))

        self.image.blit(self.cancel_button.image, (0, self.size[1] - self.cancel_button.get_height()))
        self.image.blit(self.end_turn_button.image,
                        (0, self.size[1] - self.cancel_button.get_height() - self.end_turn_button.get_height() - 2))
        self.image.blit(self.quit_button.image,
                        (0, self.size[1] - self.end_turn_button.get_height() - self.cancel_button.get_height() - self.quit_button.get_height() - 4))
        self.image.blit(self.menu_button.image,
                        (0, self.size[1] - self.end_turn_button.get_height() - self.cancel_button.get_height() - self.quit_button.get_height() - self.menu_button.get_height() - 6))   
        #self.image.blit(self.option_button.image,
        #                (0, self.size[1] - self.end_turn_button.get_height() - self.cancel_button.get_height() - self.quit_button.get_height() - self.menu_button.get_height() - self.menu_button.get_height() - 8))
        
        self.image.blit(self.right_panel, self.right_panel_position)

        if self.unit_panel:
            self.image.blit(self.unit_panel, self.unit_panel_position)

        if self.right_panel_state == 1:
            self.right_panel_position.move_ip(-20, 0)
            if self.right_panel_position.x < self.max_left_position:
                self.right_panel_state = 2

        if self.right_panel_state == 3:
            self.right_panel_position.move_ip(20, 0)
            if self.right_panel_position.x > self.max_right_position:
                self.right_panel_state = 0

#=================================================================
    def redraw_right_panel(self):
        scrx, scry = pygame.display.get_surface().get_size()
        self.right_panel = pygame.Surface((200, 400), flags=pygame.SRCALPHA)
        self.right_panel.fill(pygame.Color(0, 0, 0, 200))
        if self.right_panel_position is None:
            self.right_panel_position = pygame.Rect((scrx, 30), (300, 400))
            self.max_left_position = scrx - 200
            self.max_right_position = scrx

        btns = pygame.Surface((160, 40 * len(self.unit_array)), flags=pygame.SRCALPHA)
        #btns.fill(Palette.black_alpha)

        for i in range(len(self.unit_array)):
            recruit_btn = RecruitButton((40, i * 40))
            TestClass = GI.game_core.add_unit((-100, -100), self.unit_array[i], -1, True)
            btns.blit(TestClass.image, (0, i * 40))
            pygame.draw.rect(btns, Palette.black, pygame.Rect(0, i * 40, 32, 32), 1)
            btns.blit(recruit_btn.image, recruit_btn.rect)
            self.btn_array.append(recruit_btn)

        self.right_panel.blit(btns, (20, 20))

        #print self.enter_button_position
        self.enter_button = TownButton(self.enter_button_position, "images/enter_town.png")

        if not self.enter_button_disabled:
            self.right_panel.blit(self.enter_button.image, self.enter_button_position)

        self.leave_button = TownButton(self.leave_button_position, "images/leave_town.png")
        if not self.leave_button_disabled:
            self.leave_button.image.set_alpha(127)
            self.right_panel.blit(self.leave_button.image, self.leave_button_position)

        self.image.blit(self.right_panel, self.right_panel_position)

    def set_enter_disabled(self, value):
        self.enter_button_disabled = value
        self.redraw_right_panel()

    def set_leave_disabled(self, value):
        self.leave_button_disabled = value
        self.redraw_right_panel()

    def show_right_panel(self):
        if not GI.ai.working:
            self.unit_panel = None
            self.right_panel_state = 1
            self.redraw()

    def hide_right_panel(self):
        self.castle_active = False
        self.right_panel_state = 3
        self.redraw()

# ============================================================
    def show(self, text, cancelable=None, header = "Info:\n"):
        if GI.ai.working:
            return
        self.unit_panel = None
        self.text_buffer.append(text)
        if self.text_buffer[0].strip() != "Info:" and header == "Info:\n":
            self.text_buffer.insert(0, "Info:\n")
        else:
            self.text_buffer.insert(0, header)
        if not cancelable is None:
            self.cancelable = cancelable
        self.window_opened = True
        self.dirty_flag = True

    def hide(self):
        if self.cancelable:
            self.window = pygame.Surface(self.size, flags=pygame.SRCALPHA)
            self.window_opened = False
            self.text_buffer = list()
        else:
            pygame.quit()
            system("python GameLauncher.py")

    def draw_buffer(self):
        self.dirty_flag = False
        #print "window buffer is %s" % self.text_buffer
        px = self.rect_size.x + 30
        py = self.rect_size.y + 10
        k = 0
        self.window = pygame.Surface((640, 480), flags=pygame.SRCALPHA)
        self.window.fill(Palette.black_alpha)
        
        #pygame.draw.rect(self.window, Palette.dark_yellow, self.rect_size, 2)
        scroll = pygame.image.load("images/scroll.png").convert_alpha()
        self.window.blit(scroll,(0,0))

        #processing header
        header = self.text_buffer[0].strip()
        header_surf = pygame.font.Font("fonts/Seagram tfb.ttf", 19).render(header, 3, Palette.black)       
        rx = self.rect_size.x + (self.rect_size.width - header_surf.get_width()) / 2
        self.window.blit(header_surf, (rx, py))
        py += header_surf.get_height() + 5

        if self.cancelable == False:
            btn = UI.Button.Button("Main Menu", 0, 0)
            self.window.blit(btn.image, (200, 350))
            self.back_to_main_rect = btn.image.get_rect()
    
        #processing other text
        left_text = self.text_buffer[1:]
        for x in left_text:
            my_text = x.strip()
            for sentence in my_text.split("\n"):
                #print "processing sentence \"%s\"..." % sentence
                surf = pygame.font.Font("fonts/Seagram tfb.ttf", 16).render(sentence, 3, Palette.black)
                self.window.blit(surf, (px, py))
                py += surf.get_height() + 3

        self.image.blit(self.window, (0, 0))
#=========================================================================
#all related to unit info

    def show_unit_panel(self, unit):
        
        if not isinstance(unit,Unit):
            return

        play(self.yes_sir_sound)

        self.unit_panel = pygame.Surface((400, 100), flags=pygame.SRCALPHA)
        self.unit_panel.fill(Palette.black_alpha)

        image = pygame.image.load(unit.link)
        image = pygame.transform.scale(image, (64,64))
        self.unit_panel.blit(image, (18, 18))
        
        pygame.draw.rect(self.unit_panel, Palette.dark_yellow, pygame.Rect(0, 0, 400, 99), 2)

        #create text
        unit_attack = pygame.font.SysFont(None, 22).render("Hit points: %s" % unit.attack, 3, Palette.dark_yellow)
        self.unit_panel.blit(unit_attack, (110, 15)) 
        
        unit_defense = pygame.font.SysFont(None, 22).render("Defense: %s" % unit.defense, 3, Palette.dark_yellow)
        self.unit_panel.blit(unit_defense, (110, 45)) 
        
        unit_health = pygame.font.SysFont(None, 22).render("Health: %s/%s" % (unit.actual_health,unit.health), 3, Palette.dark_yellow)
        self.unit_panel.blit(unit_health, (110, 75)) 

        unit_movement = pygame.font.SysFont(None, 22).render("Movements: %s" % unit.movement, 3, Palette.dark_yellow)
        self.unit_panel.blit(unit_movement, (250, 15)) 
        
        unit_attack_range = pygame.font.SysFont(None, 22).render("Attack Range: %s" % unit.attack_range, 3, Palette.dark_yellow)
        self.unit_panel.blit(unit_attack_range, (250, 45)) 
        
        unit_level = pygame.font.SysFont(None, 22).render("Level: %s" % unit.level, 3, Palette.dark_yellow)
        self.unit_panel.blit(unit_level, (250, 75))

        self.unit_panel_state = 1

#=========================================================================
#all related to town
    def show_town_panel(self, town):
        
        if not isinstance(town,Town):
            return

        self.unit_panel = pygame.Surface((400, 100), flags=pygame.SRCALPHA)
        self.unit_panel.fill(Palette.black_alpha)

        image = pygame.image.load("images/town.gif")
        image = pygame.transform.scale(image, (64,64))
        self.unit_panel.blit(image, (18, 18))
        
        pygame.draw.rect(self.unit_panel, Palette.dark_yellow, pygame.Rect(0, 0, 400, 99), 2)

        #create text
        town_loyalty = pygame.font.SysFont(None, 22).render("Loyalty: %s" % town.loyalty, 3, Palette.dark_yellow)
        self.unit_panel.blit(town_loyalty, (110, 45)) 
        
        self.unit_panel_state = 1

#=========================================================================
#all related to castle right menu
    def show_castle_panel(self):
        if GI.ai.working:
            return

        self.unit_panel = None
        self.castle_active = True
        self.right_panel = pygame.Surface((200, 400), flags=pygame.SRCALPHA)
        self.right_panel.fill(Palette.black_alpha)
        unit_panel = pygame.Surface((3 * 32, 3 * 32))

        #create text
        town_units = pygame.font.SysFont(None, 22).render("Units in castle:", 3, Palette.dark_yellow)
        lbl_w = town_units.get_width()
        #print lbl_w
        self.right_panel.blit(town_units, ((200 - lbl_w) / 2, 30))

        self.units = GI.main_castle.units_inside.get_units()
        total_units = len(self.units)
        for l in range(0, 9):
            tmp = pygame.Surface((32, 32))
            if l < total_units:
                tmp.blit(self.units[l].image, (0, 0))
            else:
                tmp.fill(Palette.gray)
            pygame.draw.rect(tmp, Palette.black, pygame.Rect(0, 0, 32, 32), 2)
            unit_panel.blit(tmp, ((l % 3) * 32, (l / 3) * 32))
        lbl_toughness = pygame.font.SysFont(None, 22).render("Toughness: %s" % GI.main_castle.toughness, 3, Palette.dark_yellow)
        lbl_w = town_units.get_width()
        self.right_panel.blit(lbl_toughness, ((180 - lbl_w) / 2, 200))

        self.right_panel.blit(unit_panel, (52, 60))
        self.right_panel_state = 1

    def process_castle_menu(self, evt):
        tmp_rect = pygame.Rect(0, 0, 96, 96)
        px, py = evt.pos
        px -= self.right_panel_position.x + 52
        py -= self.right_panel_position.y + 60
        cx, cy = px / 32, py / 32
        num = cy * 3 + cx
        if tmp_rect.collidepoint((px, py)):
            #print "clicked on num=%s" % num
            total = len(self.units)
            #print "total army is %s" % total
            if num >= total:
                return
            GI.selected_unit = self.units[num]
            #print "selected unit: %s" % GI.selected_unit
            GI.game_core.leave_castle()

#=========================================================================
# processing clicks, etc
    def process_right_panel(self, evt):
        px = evt.pos[0] - self.right_panel_position.x - 20
        py = evt.pos[1] - self.right_panel_position.y

        if self.enter_button.rect.collidepoint((px, py)) and not self.enter_button_disabled:
            #print "enter button pressed!"
            if not self.castle_active:
                GI.game_core.enter_town()
                return
            GI.game_core.enter_castle()
            return

        if self.leave_button.rect.collidepoint((px, py)) and not self.leave_button_disabled:
            #print "leave button pressed!"
            GI.game_core.leave_town()
            return

        k = 0
        for x in self.btn_array:
            px, py = x.rect.x + self.right_panel_position.x + 20, x.rect.y + self.right_panel_position.y + 20
            tmp = pygame.Rect((px, py), (x.rect.width, x.rect.height))
            if tmp.collidepoint(evt.pos):
                break
            k += 1
        #print "collide with button #",
        if k < len(self.btn_array):
            if GI.game_core.recruit(self.unit_array[k]):
                play(self.trumpet_sound)
#================================================

    def show_options_menu(self):
        self.show("", header = "Options")

#================================================
    def show_transparent_layer(self):
        #we'll use it to prevent mouse clicking on map while moving
        self.tl_active = True

    def hide_transparent_layer(self):
        if GI.ai.working:
            return
        self.tl_active = False

#================================================
    def process_event(self, evt):
        #check if invisible layer over the window is active
        if self.tl_active:
            return False

        #Quit Game
        if evt.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        #right panel
        if evt.type == pygame.MOUSEBUTTONUP and self.cancelable and self.right_panel_position.collidepoint(evt.pos):
            #print "right panel pressed"
            if self.castle_active:
                self.process_castle_menu(evt)
                return False
            self.process_right_panel(evt)
            return False

        #check if window onstage
        if self.window_opened:
            if evt.type == pygame.MOUSEBUTTONUP and evt.button == 1:
                self.hide()
                self.redraw()
            return False

        if self.right_panel_state == 2:
            if evt.type == pygame.MOUSEBUTTONUP and evt.button == 1:
                self.hide_right_panel()
            return False

        #check if buttons
        ## end turn button
        if evt.type == pygame.MOUSEBUTTONUP and self.skip_rect.collidepoint(evt.pos):
            #print "End turn pressed"
            GI.game_core.change_turn()
            return False
        
        ## quit button 
        if evt.type == pygame.MOUSEBUTTONUP and self.quit_rect.collidepoint(evt.pos):
            #print "Quit Game"
            pygame.quit()
            sys.exit()
        
        ## main menu
        if evt.type == pygame.MOUSEBUTTONUP and self.menu_rect.collidepoint(evt.pos):
            pygame.quit()
            system("python GameLauncher.py")
        
        # show option menu
        #if evt.type == pygame.MOUSEBUTTONUP and self.option_rect.collidepoint(evt.pos):
        #    self.show_options_menu()

        ## cancel button
        if evt.type == pygame.MOUSEBUTTONUP and self.cancel_rect.collidepoint(evt.pos):
            #print "Cancel pressed"
            if self.reset_turn:
                self.show("You can't reset more than once per turn!")
                return False

            if GI.selected_unit:
                GI.worldGrid.update_from_source(GI.selected_unit.position)
                GI.worldGrid.redraw(clearing=True)

            GI.game_core.restore_from_backup()
            self.reset_turn = True
            return False
        
		#check unit grid
        if evt.type == pygame.MOUSEBUTTONUP and GI.unitGrid.defaultSize.collidepoint(evt.pos):
            #print "unit grid pressed"
            GI.unitGrid.calc_press(evt.pos)
            return False

        if evt.type == pygame.MOUSEBUTTONUP and evt.button == 1:
            return True

        if evt.type == pygame.MOUSEBUTTONUP and evt.button == 3:
            return True

        if evt.type == pygame.KEYDOWN or evt.type == pygame.KEYUP:
            if evt.key == pygame.K_q:
                pygame.quit()
                sys.exit()
            return True

        if evt.type == pygame.MOUSEMOTION:
            return True

        return False

#=========================================================================


class TownButton():
    image = None
    rect = None

    def __init__(self, pos, image):
        self.image = pygame.image.load(image).convert_alpha()
        self.rect = pygame.Rect(pos, self.image.get_size())


class RecruitButton(TownButton):
    def __init__(self, pos):
        TownButton.__init__(self, pos, "images/recruit.png")
