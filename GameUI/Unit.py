from GameUI.ActiveTile import ActiveTile
from GameMechanics.GameSound import load_sound
from GameMechanics.GameSound import play
from GameMechanics.ColorPalette import ColorPalette as Palette
from GameMechanics.GameInfo import GameInfo as GI
from GameUI import Missile

import pygame

__author__ = 'dark-wizard'


class Unit(ActiveTile):
    ANIMATION_LENGTH = 1000

    attack = 0
    defense = 0
    attack_range = 0
    movement = 0
    health = 0
    actual_health = health
    base_sprite_name = ""
    display_name = ""
    level = 1

    #every two elements is an animation
    walk_animation = list()         # list of surfaces
    walk_src = list()               # list of images, which surfaces are created from

    fight_animation = list()
    playing_animation = False
    frames = list()
    frame_names = list()
    current_frame = 0
    time_passed = ANIMATION_LENGTH
    needed_time = ANIMATION_LENGTH       # every 100 mills we change frame

    #position in animation array
    position_names = ["fr", "bk", "lf", "rt"]
    DOWN = 0
    UP = 2
    LEFT = 4
    RIGHT = 6

    def __init__(self, image, pos):
        self.walk_sound = load_sound("walk")
        self.die_sound = load_sound("death")
        self.walk_animation = list()
        path_str = "images/" + image + "/"
        self.base_sprite_name = image
        ActiveTile.__init__(self, path_str + image + "_fr1.gif", pos)
        #print "i am %s and i'm loading:" % self

    def load_tiles(self, walk_surf, walk_names):
        self.walk_animation = walk_surf
        self.walk_src = walk_names

    def redraw(self):
        #print "redrawing..."
        #self.change_frames()
        tmp = self.get_hp_surface()
        self.image.blit(tmp, (0, 0))

    def get_hp_surface(self):
        hp_surf = pygame.Surface((32, 5), flags=pygame.SRCALPHA)
        pygame.draw.rect(hp_surf, Palette.red, pygame.Rect((0, 0), (32, 5)), 1)
        bar_width = float(self.actual_health) / self.health * 32
        # #print "bar width is ", bar_width
        pygame.draw.rect(hp_surf, Palette.red, pygame.Rect((1, 1), (bar_width, 3)))
        self.image.blit(hp_surf, (0, 0))
        return hp_surf.copy()

    def damage(self, hp):
        if hp < 0:
            hp = 0
        self.actual_health -= hp
        #print "receiving damage", hp, ",actual health is", self.actual_health
        #print "percentage is ", float(self.actual_health) / self.health * 32
        if self.actual_health <= 0:
            self.die()

    def level_up(self, plus = 0):
        self.attack += 2 + plus
        self.defense += 2 + plus
        self.health *= 1.25 
        self.health = int(self.health)
        self.actual_health = self.health
        self.level += 1

    def die(self):
        play(self.die_sound, True)
        #print "dying :("
        self.hidden = True
        self.player_index = -1

    def update_info(self, args=None):
        if not args is None:
            self.info = args
        info = "%s\nlevel:%s\nattack:%s\ndefense:%s\nattack_range:%s\nmovement:%s\nhealth:%s\nactual_health:%s\n" % (
            self.display_name, self.level, self.attack, self.defense, self.attack_range, self.movement, self.health, self.actual_health)
        self.info = info

    def heal(self):
        if self.actual_health < self.health:
            self.actual_health += self.health * 0.01
        if self.actual_health > self.health:
            self.actual_health = self.health

    def change_frames(self, every_redraw=False):
        if self.playing_animation:
            #print "we're using this frames to update: %s" % self.frame_names
            self.time_passed += GI.time_passed
            if not GI.ai.working:
                play(self.walk_sound)
            #print self.time_passed
            if self.time_passed > self.needed_time or every_redraw:
                #print "time to change frame!"
                self.time_passed = 0
                self.current_frame += 1
                if self.current_frame == len(self.frames):
                    self.current_frame = 0
                self.image = pygame.Surface((32, 32), flags=pygame.SRCALPHA)
                #print "frame # ", self.current_frame
                self.image.blit(self.frames[self.current_frame], (0, 0))
                #print "new image loaded is %s" % self.frame_names[self.current_frame]

    def play_walk_animation(self, position):
        self.playing_animation = True
        self.time_passed = self.ANIMATION_LENGTH
        self.frames = self.walk_animation[position:position + 2]
        self.frame_names = self.walk_src[position:position + 2]
        #self.current_frame = 1

    def stop_walk_animation(self):
        self.playing_animation = False
        self.time_passed = self.ANIMATION_LENGTH
