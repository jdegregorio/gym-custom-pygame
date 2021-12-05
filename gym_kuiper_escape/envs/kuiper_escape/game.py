"""
Kuiper Escape

A game developed in the pygame framework. The objective is to avoid the 
asteroids/rocks for as long as possible while the rate of rocks increases 
steadily over time.

"""
# Standard imports
import sys
import os
import random
import math

# 3rd party imports
import pygame
from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    QUIT,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT
)

# Local imports
path_components = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, path_components)
from player import Player
from rock import Rock

class Game:
    def __init__(
        self, 
        mode='human',
        lives=3,
        rate_start=2,  # Number of rocks/second generated
        rate_increment=50  # Add additional rock/second every N seconds
    ):
        # Initialize pygame
        pygame.init()
        self.mode = mode
        self.font = pygame.font.SysFont("monospace", 24)
        self.score = 0
        self.lives = lives
        self.rate_start = rate_start
        self.rate_increment = rate_increment
        self.clock = pygame.time.Clock()

        # Define constants for the screen width and height
        if self.mode == 'human':
            self.screen_mode = pygame.SHOWN
        else:
            self.screen_mode = pygame.HIDDEN
        self.screen_width = 800
        self.screen_height = 800
        self.screen_dims = (self.screen_width, self.screen_height)
        self.framerate = 50
        self.screen = pygame.display.set_mode(
            self.screen_dims, 
            flags=self.screen_mode
        )

        # Instantiate player and sprite groups
        self.player = Player(screen_dims=self.screen_dims, lives=self.lives)
        self.rocks = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)


    def step_frame(self, action):

        # Add rocks, increase rate over time
        thres  = (1 / self.framerate) * (self.rate_start + (self.score / self.rate_increment))
        if random.random() < thres:
            new_rock = Rock(screen_dims=self.screen_dims)
            self.rocks.add(new_rock)
            self.all_sprites.add(new_rock)

        # Update sprite positions
        self.player.update(action)
        self.rocks.update()

        # Check for collisions, deduct player life
        collisions = pygame.sprite.spritecollide(self.player, self.rocks, dokill=False)
        for rock in collisions:
            rock.kill()
            self.player.die()

        # Check if player has any remaining lives
        if self.player.lives == 0:
            self.running = False

        # Update score
        self.score += 1 / self.framerate


    def get_action(self, pressed_keys):
        up = pressed_keys[K_UP]
        right = pressed_keys[K_RIGHT]
        down = pressed_keys[K_DOWN]
        left = pressed_keys[K_LEFT]
        n_pressed = sum([up, right, down, left])
        if n_pressed < 0 or n_pressed > 2:
            action = 0
        elif n_pressed == 1 and up:
            action = 1
        elif n_pressed == 2 and up and right:
            action = 2
        elif n_pressed == 1 and right:
            action = 3
        elif n_pressed == 2 and right and down:
            action = 4
        elif n_pressed == 1 and down:
            action = 5
        elif n_pressed == 2 and down and left:
            action = 6
        elif n_pressed == 1 and left:
            action = 7
        elif n_pressed == 2 and left and up:
            action = 8
        else:
            action = 0
        return action

    
    def turn_on_screen(self):
        self.screen = pygame.display.set_mode(
            self.screen_dims, 
            flags=pygame.SHOWN
        )


    def render_screen(self):
        self.screen.fill((0, 0, 0))
        info_score = self.font.render("Score = " + str(math.floor(self.score)), 1, (255, 255, 255))
        info_lives = self.font.render("Lives =  " + str(self.player.lives), 1, (255, 255, 255))
        self.screen.blit(info_score, (5, 10))
        self.screen.blit(info_lives, (self.screen_width - 200, 10))
        for entity in self.all_sprites:
            self.screen.blit(entity.surf, entity.rect)

        # Update the display
        pygame.display.flip()


    def play(self):

        # Variable to keep the main loop running
        self.running = True

        # Main loops
        while self.running:
            # Loop through event queue
            for event in pygame.event.get():
                # Check for KEYDOWN event
                if event.type == KEYDOWN:
                    # If the Esc key is pressed, then exit the main loop
                    if event.key == K_ESCAPE:
                        self.running = False
                # Check for QUIT event. If QUIT, then set running to false.
                elif event.type == QUIT:
                    self.running = False

            # Step frame
            pressed_keys = pygame.key.get_pressed()
            action = self.get_action(pressed_keys)
            self.step_frame(action)
            self.render_screen()

            # Set framerate
            self.clock.tick(self.framerate)
