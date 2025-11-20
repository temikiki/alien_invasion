import sys
from time import sleep

import pygame
from settings import Settings
from game_stats import GameStats
from button import Button
from ship import Ship
from scoreboard import ScoreBoard
from bullet import Bullet
from alien import Alien

class AlienInvasion:
    """"Overall class to manage game assets and behavior"""
    def __init__(self):
        """Initilize the game, and creat game resources"""
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()
        #set background color
       # self.bg_color =(230,230,230)
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")
        #Create an instance to store a game statistics
        #and create a scoreboard.
        self.stats = GameStats(self)
        self.sb = ScoreBoard(self)
        self.ship =Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self._create_fleet()

        #Start Alien Invasion in an active state
        self.game_active = False
        # MAke the Play buttton
        self.play_button = Button(self, "Play")
   
    def run_game(self):
        """Start the main loop for the game"""
        while True:
            #watch for keyboard and mouse events.
            self.check_events()
            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            self._update_screen()          
            self.clock.tick(60)

    def _create_fleet(self):
        """create the fleet of aliens"""
        #create an alien and keep adding untill there is no room left
        #Spacing between aliens is one alien width and one alien height
        alien =Alien(self)
        alien_width, alien_height = alien.rect.size

        current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height- 4 * alien_height):
            while current_x < (self.settings.screen_width -2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width

            #finished a row; reset x value, and increment y value
            current_x = alien_width
            current_y += 2*alien_height
            
    def _create_alien(self, x_position,y_position):
        """create an alien and place it in the row"""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _ship_hit(self):
        """Respond to the ship being hit by an alien"""
        if self.stats.ships_left >0:
            #Drecrement ships left.
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            #Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()

            #create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()
            
            #pause
            sleep(0.5)
        else:
            self.game_active = False
            pygame.mouse.set_visible(True)
            self.play_button = Button(self, "Play Again")

    # def _update_aliens(self):
    #     """update the position of all aliens in the fleet"""
    #     self.aliens.update()

    def _check_fleet_edges(self):
        """respond appropriately if any aliens have reached an edge"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
    
    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_aliens(self):
        """check if the fleet is at an edge, the update positions"""
        self._check_fleet_edges()
        self.aliens.update()
        #Look for alien-Ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Look for aliens hitting the bottom of the screen
        self._check_aliens_bottom()

    def _check_aliens_bottom(self):
        """check if any aliens have reached the bottom of the screen."""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                # Treat this the same as if the ship got hit
                self._ship_hit()
                break

    def _update_bullets(self):
        self.bullets.update()
        """Update position of bullets and gets rid of old bullets"""
        self._check_bullet_alien_collisions()
        #Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
             if bullet.rect.bottom <=0:
                self.bullets.remove(bullet)
           ## print(len(self.bullets))

    def _check_bullet_alien_collisions(self):
        """Respond to bullet-allien collisions """
        # Check for any bullets that have hit aliens
        #if so, get rid of the bullet and the aliens
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            #Destroy existing buullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            #Increase level.
            self.stats.level += 1
            self.sb.prep_level()

    def check_events(self):
        """respond to keypresses and mouse events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                 self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self.check_play_button(mouse_pos)
               
    def check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            #REset the game settings
            self.settings.initialize_dynamic_settings()
            #Reset the game statistics.
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            self.game_active = True

            #hide the mouse cursor
            pygame.mouse.set_visible(False)

            #Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()

            #Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()

    def _check_keydown_events(self, event):
        """respond to keypress"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self.fire_bullet()
    
    def _check_keyup_events(self, event):
         """respond to key release"""
         if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
         elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        
        
    def fire_bullet(self):
        """create a new bullet and add it to the bullets group"""
        if len(self.bullets)< self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_screen(self):
          #redraw the screen during each pass through the loop
            self.screen.fill(self.settings.bg_color)
            for bullet in self.bullets.sprites():
                bullet.draw_bullet()
            self.ship.blitme()
            self.aliens.draw(self.screen)

            #Draw the score information
            self.sb.show_score()

            # draw the play butoon if the game is inactive
            if not self.game_active:
                self.play_button.draw_button()

         # make the most recently drawn screen visible.
            pygame.display.flip()
    
    
if __name__ == '__main__':
    # make the game instance, and run the game .
    ai = AlienInvasion()
    ai.run_game()

