# Standard imports
import os

# 3rd party imports
import pygame
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT
)

# Construct path to assets
path_base = os.path.dirname(os.path.realpath(__file__))
path_asset = os.path.join(path_base, 'assets/spaceship.png')

class Player(pygame.sprite.Sprite):
    def __init__(self, screen_size, lives=3, speed=5):
        super(Player, self).__init__()
        self.screen_size = screen_size
        self.lives = lives
        self.speed = speed
        self.surf = pygame.image.load(path_asset)
        aspect_ratio = self.surf.get_height() / self.surf.get_width()
        scaled_height = self.screen_size * 0.05
        scaled_width = scaled_height * aspect_ratio
        self.surf = pygame.transform.scale(
            self.surf, (scaled_height, scaled_width)
        )
        self.surf = self.surf.convert_alpha()
        self.rect = self.surf.get_rect(
            center = (
                self.screen_size  / 2, 
                self.screen_size / 2
            )
        )

    # Move the sprite based on user keypresses
    def update(self, action):
        if action == 1:
            self.rect.move_ip(0, -self.speed)
        if action == 2:
            self.rect.move_ip(self.speed, 0)
        if action == 3:
            self.rect.move_ip(0, self.speed)
        if action == 4:
            self.rect.move_ip(-self.speed, 0)
        if action == 5:
            self.rect.move_ip(self.speed, -self.speed)
        if action == 6:
            self.rect.move_ip(self.speed, self.speed)
        if action == 7:
            self.rect.move_ip(-self.speed, self.speed)
        if action == 8:
            self.rect.move_ip(-self.speed, -self.speed)

        # Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.screen_size:
            self.rect.right = self.screen_size
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= self.screen_size:
            self.rect.bottom = self.screen_size

    def die(self):
        self.lives -= 1
