import pygame
class Ship:
    """a class to manage the ship"""
    def  __init__(self,ai_game):
        """initialize the ship and set its starting position"""
        self.screen = ai_game.screen
        self.screen_rect = ai_game.screen.get_rect()
        self.settings = ai_game.settings

        #load the ship image and get its rect.
        self.image = pygame.image.load('image/ship.bmp')
        self.rect = self.image.get_rect()

        #start each new ship at the bottom center of the screen
        self.rect.midbottom = self.screen_rect.midbottom

        #store a float for the ship's exact horizontal position
        self.x = float(self.rect.x)
        #Movement flag; start with a ship that is not moving.
        self.moving_right = False
        self.moving_left = False
        
    
    def update(self):
        """Update the ship's postion based on the movement flag."""
        #update the ship,s x value, not the object
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed 
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed
        #update rect object from self.x.

        self.rect.x = self.x
    
    
    def blitme(self):
        """draw the ship at its current location"""
        self.screen.blit(self.image, self.rect)