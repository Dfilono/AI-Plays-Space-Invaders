# -*- coding: utf-8 -*-
"""
Created on Thu Oct 20 12:12:08 2022

@author: filon
"""
import pygame
import sys
from player import Player
import obstacle
from alien import Alien, Extra
from random import choice, randint
from laser import Laser

class Game:
    def __init__(self):
        #Player setup
        player_sprite = Player((screen_w/2, screen_h), screen_w, 5)
        self.player = pygame.sprite.GroupSingle(player_sprite)
        
        #health and score
        self.lives = 3
        self.live_surf = pygame.image.load('player.png').convert_alpha()
        self.live_x_start_pos = screen_w - (self.live_surf.get_size()[0]*2 + 20)
        self.score = 0
        self.font = pygame.font.Font('Pixeled.ttf', 20)
        
        #obstacle setup
        self.shape = obstacle.shape
        self.block_size = 6
        self.blocks = pygame.sprite.Group()
        self.obstacle_amount = 4
        self.obstacle_x_pos = [num * (screen_w/self.obstacle_amount) for num in range(self.obstacle_amount)]
        self.create_muli_obstacles(*self.obstacle_x_pos, x_start = screen_w/15, y_start = 480)
        
        #alien setup
        self.aliens = pygame.sprite.Group()
        self.alien_lasers = pygame.sprite.Group()
        self.alien_setup(rows = 6, cols = 8)
        self.alien_direction = 1
        
        #Extra setup
        self.extra = pygame.sprite.Group()
        self.extra_spawn_time = randint(40,80)
        
        #Audio
        music = pygame.mixer.Sound('music.wav')
        music.set_volume(0.2)
        music.play(loops = -1)
        self.laser_sound = pygame.mixer.Sound('laser.wav')
        self.laser_sound.set_volume(0.5)
        self.explosion_sound = pygame.mixer.Sound('explosion.wav')
        self.explosion_sound.set_volume(0.3)
        
    def create_obstacle(self, x_start, y_start, offset_x):
        for row_i, row in enumerate(self.shape):
            for col_i, col in enumerate(row):
                if col == 'x':
                    x = x_start + col_i * self.block_size + offset_x
                    y = y_start + row_i * self.block_size
                    block = obstacle.Block(self.block_size,(241,79,80), x, y)
                    self.blocks.add(block)
    
    def create_muli_obstacles(self, *offset, x_start, y_start):
        for offset_x in offset:
            self.create_obstacle(x_start, y_start, offset_x)
            
    def alien_setup(self, rows, cols, x_distance = 60, y_distance = 48, x_offset = 70, y_offset = 100):
        for row_i, row in enumerate(range(rows)):
            for col_i, col in enumerate(range(cols)):
                x = col_i*x_distance + x_offset
                y = row_i*y_distance + y_offset
                
                if row_i == 0:
                    alien_sprite = Alien('yellow', x, y)
                elif 1 <= row_i <= 2:
                    alien_sprite = Alien('green', x, y)
                else:
                    alien_sprite = Alien('red', x, y)
                
                self.aliens.add(alien_sprite)
    
    def alien_pos_check(self):
        all_aliens = self.aliens.sprites()
        for alien in all_aliens:
            if alien.rect.right >= screen_w:
                self.alien_direction = -1
                self.alien_move_down(2)
            elif alien.rect.left <= 0:
                self.alien_direction = 1
                self.alien_move_down(2)
    
    def alien_move_down(self, distance):
        if self.aliens:
            for alien in self.aliens:
                alien.rect.y += distance
                
    def alien_shoot(self):
        if self.aliens.sprites():
            random_alien = choice(self.aliens.sprites())
            laser_sprite = Laser(random_alien.rect.center, 6, screen_h)
            self.alien_lasers.add(laser_sprite)
            self.laser_sound.play()
    
    def extra_alien_timer(self):
        self.extra_spawn_time -= 1
        if self.extra_spawn_time <= 0:
            self.extra.add(Extra(choice(['left','right']), screen_w))
            self.extra_spawn_time = randint (400, 800)
    
    def collision_checks(self):
        if self.player.sprite.lasers:
            for laser in self.player.sprite.lasers:
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()
                
                aliens_hit = pygame.sprite.spritecollide(laser, self.aliens, True)
                if aliens_hit:
                    for alien in aliens_hit:
                        self.score += 1
                    laser.kill()
                    self.explosion_sound.play()
                
                if pygame.sprite.spritecollide(laser, self.extra, True):
                    self.score += 500
                    laser.kill()
                    
        if self.alien_lasers:
            for laser in self.alien_lasers:
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()
                
                if pygame.sprite.spritecollide(laser, self.player, False):
                    laser.kill()
                    self.lives -= 1
                    if self.lives <= 0:
                        pygame.quit()
                        sys.exit()
    
        if self.aliens:
            for alien in self.aliens:
                pygame.sprite.spritecollide(alien, self.blocks, True)
            
            if pygame.sprite.spritecollide(alien, self.player, False):
                pygame.quit()
                sys.exit()
    
    def display_lives(self):
        for life in range(self.lives -1):
            x = self.live_x_start_pos + (life * (self.live_surf.get_size()[0] + 10))
            screen.blit(self.live_surf, (x, 8))
    
    def display_score(self):
        score_surf = self.font.render(f'score: {self.score}', False, 'white')
        score_rect = score_surf.get_rect(topleft = (10, -10))
        screen.blit(score_surf, score_rect)
        
    def victory_message(self):
        if not self.aliens.sprites():
            victory_surf = self.font.render('You Won!', False, 'white')
            victory_rect = victory_surt.get_rect(center = (screen_w/2, screen_h/2))
            screen.blit(victory_surf, victory_rect)
    
    def run(self):
        self.player.update()
        self. alien_lasers.update()
        self.extra.update()
        
        self.aliens.update(self.alien_direction)
        self.alien_pos_check() 
        self.extra_alien_timer()
        self.collision_checks()
		
        self.player.sprite.lasers.draw(screen)
        self.player.draw(screen)
		
        self.blocks.draw(screen)
        self.aliens.draw(screen)
        self.alien_lasers.draw(screen)
        self.extra.draw(screen)
        self.display_lives()
        self.display_score()
        self.victory_message()
        
class CRT:
    def __init__(self):
        self.tv = pygame.image.load('tv.png').convert_alpha()
        self.tv = pygame.transform.scale(self.tv,(screen_w, screen_h))
        
    def create_crt_lines(self):
        line_h = 3
        line_amt = int(screen_h/line_h)
        for line in line_amt:
            y_pos = line*line_h
            pygame.draw.line(self.tv, 'black', (0, y_pos), (screen_w, y_pos), 1)
    
    def draw(self):
        self.tv.set_alpha(randint(75,90))
        self.create_crt_lines()
        screen.blit(self.tv, (0,0))
        
if __name__ == '__main__':
    pygame.init()
    screen_w = 600
    screen_h = 600
    screen = pygame.display.set_mode((screen_w, screen_h))
    clock = pygame.time.Clock()
    game = Game()
    crt = CRT()
    
    ALIENLASER = pygame.USEREVENT +1
    pygame.time.set_timer(ALIENLASER, 800)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == ALIENLASER:
                game.alien_shoot()
                
        screen.fill((30,30,30))
        game.run()
        #crt.draw()
        
        pygame.display.flip()
        clock.tick(60)
        
        