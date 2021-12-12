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
        self.face = random.choice(['top', 'right', 'bottom', 'left'])
        self.angle_limit = 0.1*math.pi
        self.angle = random.uniform(self.angle_limit, math.pi - self.angle_limit)
        if self.face == 'top':
            self.angle += math.pi
            self.x = random.randint(0, self.screen_size)
            self.y = -self.size / 2
        elif self.face == 'right':
            self.angle += 0.5 * math.pi
            self.x = self.screen_size + (self.size) / 2
            self.y = random.randint(0, self.screen_size)
        elif self.face == 'bottom':
            self.angle = self.angle
            self.x = random.randint(0, self.screen_size)
            self.y = self.screen_size + (self.size / 2)
        elif self.face == 'left':
            self.angle += 1.5 * math.pi
            self.x = -self.size / 2
            self.y = random.randint(0, self.screen_size)
        self.angle = self.angle % (2 * math.pi)
        self.dir_x = math.cos(self.angle)
        self.dir_y = math.sin(self.angle)
        self.surf = pygame.image.load(path_asset)
        self.surf = pygame.transform.scale(self.surf, (self.size, self.size))
        self.surf = self.surf.convert_alpha()
        self.rect = self.surf.get_rect(centerx = self.x, centery = self.y)

    # Update location, kill if moved off of the screen
    def update(self):
        self.x += self.speed * self.dir_x
        self.y += -self.speed * self.dir_y
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        if self.rect.right < 0:
            self.kill()
        elif self.rect.left > self.screen_size:
            self.kill()
        elif self.rect.top > self.screen_size:
            self.kill()
        elif self.rect.bottom < 0:
            self.kill()
