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
    def __init__(self, screen_dims,
        size_min=20, size_max=100, speed_min=2, speed_max=10
    ):
        super(Rock, self).__init__()
        self.screen_width = screen_dims[0] * 1.2 
        self.screen_height = screen_dims[1] * 1.2 
        self.size_min = size_min
        self.size_max = size_max
        self.size = self.size_min + random.random() * (self.size_max - self.size_min)
        self.size = random.randint(self.size_min, self.size_max)
        self.speed_min = speed_min
        self.speed_max = speed_max
        self.speed = self.speed_min + random.random() * (self.speed_max - self.speed_min)
        self.angle = random.random() * 2 * math.pi
        self.dir_x = math.cos(self.angle)
        self.dir_y = math.sin(self.angle)
        if self.dir_x > 0 and self.dir_y <= 0:
            self.face = random.choice(['left', 'top'])
        elif self.dir_x > 0 and self.dir_y > 0:
            self.face = random.choice(['left', 'bottom'])
        elif self.dir_x <= 0 and self.dir_y <= 0:
            self.face = random.choice(['right', 'top'])
        elif self.dir_x <= 0 and self.dir_y > 0:
            self.face = random.choice(['right', 'bottom'])
        if self.face == 'left':
            self.center = (-self.size / 2, random.randint(0, self.screen_height))
        elif self.face == 'right':
            self.center = (self.screen_width + (self.size / 2), random.randint(0, self.screen_height))
        elif self.face == 'top':
            self.center = (random.randint(0, self.screen_width), -self.size / 2)
        elif self.face == 'bottom':
            self.center = (random.randint(0, self.screen_width), self.screen_height + (self.size / 2))
        self.surf = pygame.image.load(path_asset)
        self.surf = pygame.transform.scale(self.surf, (self.size, self.size))
        self.surf = self.surf.convert_alpha()
        self.rect = self.surf.get_rect(center=self.center)

    # Update location, kill if moved off of the screen
    def update(self):
        self.rect.move_ip(self.speed * self.dir_x, -self.speed * self.dir_y)
        if self.rect.right < 0:
            self.kill()
        elif self.rect.left > self.screen_width:
            self.kill()
        elif self.rect.top > self.screen_height:
            self.kill()
        elif self.rect.bottom < 0:
            self.kill()
