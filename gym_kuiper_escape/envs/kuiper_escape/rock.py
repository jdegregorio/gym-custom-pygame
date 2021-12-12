# Standard imports
import os
import math
import random

# 3rd party imports
import pygame

# Construct path to assets
path_base = os.path.dirname(os.path.realpath(__file__))
path_asset = os.path.join(path_base, 'assets/asteroid.png')

class Rock(pygame.sprite.Sprite):
    def __init__(self, screen_size, 
        speed_min=2, speed_max=10,
        size_min=0.04, size_max=0.08
    ):
        super(Rock, self).__init__()
        self.screen_size = screen_size
        self.size_min = size_min
        self.size_max = size_max
        self.size = random.uniform(self.size_min, self.size_max) * self.screen_size
        self.speed_min = speed_min
        self.speed_max = speed_max
        self.speed = random.uniform(self.speed_min, self.speed_max)
        self.angle = random.random() * math.pi
        self.face = random.choice(['bottom', 'left', 'top', 'right'])
        if self.face == 'bottom':
            self.angle = self.angle
            self.dir_x = math.cos(self.angle)
            self.dir_y = math.sin(self.angle)
            # TODO: offset size so that it's possible the right comes in from the complete edge
            self.center = (random.randint(0, self.screen_size), self.screen_size + (self.size / 2))
        elif self.face == 'right':
            self.angle = self.angle + (1 * (math.pi / 4))
            self.dir_x = math.cos(self.angle)
            self.dir_y = math.sin(self.angle)
            self.center = (self.screen_size + (self.size) / 2, random.randint(0, self.screen_size))
        elif self.face == 'top':
            self.angle = self.angle + (2 * (math.pi / 4))
            self.dir_x = math.cos(self.angle)
            self.dir_y = math.sin(self.angle)
            self.center = (random.randint(0, self.screen_size), -self.size / 2)
        elif self.face == 'left':
            self.angle = self.angle + (3 * (math.pi / 4))
            self.dir_x = math.cos(self.angle)
            self.dir_y = math.sin(self.angle)
            self.center = (-self.size / 2, random.randint(0, self.screen_size))
        self.surf = pygame.image.load(path_asset)
        self.surf = pygame.transform.scale(self.surf, (self.size, self.size))
        self.surf = self.surf.convert_alpha()
        self.rect = self.surf.get_rect(center=self.center)

    # Update location, kill if moved off of the screen
    def update(self):
        self.rect.move_ip(self.speed * self.dir_x, -self.speed * self.dir_y)
        if self.rect.right < 0:
            self.kill()
        elif self.rect.left > self.screen_size:
            self.kill()
        elif self.rect.top > self.screen_size:
            self.kill()
        elif self.rect.bottom < 0:
            self.kill()
