import pygame
from GameMechanics.GameSound import load_sound
from GameMechanics.GameSound import play

class Missile:
    
    def __init__(self, __type__, __from__, __to__, __gap__ = (0,0)):
        
        from_x = __from__[0] + __gap__[0]
        from_y = __from__[1] + __gap__[1]
        to_x = __to__[0] * 32 + __gap__[0]
        to_y = __to__[1] * 32 + __gap__[1]
        self.speed = [ 0 , 0 ]

        if from_x > to_x:
            self.direction = "left" 
            self.speed[0] = -5        
        if from_x < to_x:
            self.direction = "right"
            self.speed[0] = 5        
        if from_y > to_y:
            self.direction = "up"
            self.speed[1] = -5        
        if from_y < to_y:
            self.direction = "down"
            self.speed[1] =  5
        
        self.image = pygame.image.load("images/" + __type__ + "/" + self.direction + ".png")
        self.missile = self.image.get_rect().move([from_x, from_y])
        self.target = pygame.Rect( to_x, to_y, 32, 32)
        self.battle_sound = load_sound(__type__)
        
    def show_animation(self):        
        screen = pygame.display.get_surface()
        window = screen.copy()
        play(self.battle_sound, True)        
        pygame.time.delay(500)

        while not self.missile.colliderect(self.target):
            self.missile = self.missile.move(self.speed)
            screen.blit(window,(0,0))            
            screen.blit(self.image, self.missile)
            pygame.time.delay(50)
            pygame.display.flip()

