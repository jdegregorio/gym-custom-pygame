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
        player_speed=0.5,  # portion of screen traversed in one second
        rock_rate=2,  # Number of rocks/second generated
        rock_size_min=0.04,
        rock_size_max=0.08,
        rock_speed_min=0.1,  # portion of screen traversed in one second
        rock_speed_max=0.3,  # portion of screen traversed in one second
        framerate=10
    ):
        # Initialize pygame
        pygame.init()
        pygame.display.set_caption('Kuiper Escape')
        self.mode = mode
        self.font = pygame.font.SysFont("monospace", 12)
        self.frame = 1
        self.time = 0
        self.lives = lives
        self.player_speed = player_speed
        self.rock_rate = rock_rate
        self.rock_speed_min = rock_speed_min
        self.rock_speed_max = rock_speed_max
        self.rock_size_min = rock_size_min
        self.rock_size_max = rock_size_max

        # Define constants for the screen width and height
        if self.mode == 'human':
            self.screen_mode = pygame.SHOWN
            self.include_info = True
        else:
            self.screen_mode = pygame.HIDDEN
            self.include_info = False
        self.screen_size = 512
        self.screen_dims = (self.screen_size, self.screen_size)
        self.framerate = framerate
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(
            self.screen_dims, 
            flags=self.screen_mode
        )

        # Instantiate player and sprite groups
        self.player = Player(
            screen_size=self.screen_size, 
            lives=self.lives,
            speed=self.player_speed * self.screen_size * (1 / self.framerate)
        )
        self.rocks = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)

    def step_frame(self, action):

        # Add rocks, increase rate over time
        frames_per_rock = int(self.framerate / self.rock_rate)
        if frames_per_rock < 1:
            frames_per_rock = 1
        if self.frame % frames_per_rock == 0:
            new_rock = Rock(
                screen_size=self.screen_size,
                size_min=self.rock_size_min,
                size_max=self.rock_size_max,
                speed_min=self.rock_speed_min * self.screen_size * (1 / self.framerate),
                speed_max=self.rock_speed_max * self.screen_size * (1 / self.framerate)
            )
            self.rocks.add(new_rock)
            self.all_sprites.add(new_rock)
        else:
            new_rock = None

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

        # Update screen surface
        self.update_screen()

        # Increment frame and time
        self.frame += 1
        self.time = (self.frame / self.framerate)

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
        elif n_pressed == 1 and right:
            action = 2
        elif n_pressed == 1 and down:
            action = 3
        elif n_pressed == 1 and left:
            action = 4
        elif n_pressed == 2 and up and right:
            action = 5
        elif n_pressed == 2 and right and down:
            action = 6
        elif n_pressed == 2 and down and left:
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
        self.include_info=True

    def update_screen(self):
        self.screen.fill((0, 0, 0))
        if self.include_info:
            info_score = self.font.render("Score = " + str(math.floor(self.time)), 1, (255, 255, 255))
            info_lives = self.font.render("Lives =  " + str(self.player.lives), 1, (255, 255, 255))
            self.screen.blit(info_score, (5, 10))
            self.screen.blit(info_lives, (self.screen_size - 100, 10))
        for entity in self.all_sprites:
            self.screen.blit(entity.surf, entity.rect)

    def render_screen(self):
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
            self.clock.tick_busy_loop(self.framerate)
