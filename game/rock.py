import pygame
import random
import math


class Rock(pygame.sprite.Sprite):
    def __init__(self, screen_dims):
        super(Rock, self).__init__()
        self.screen_width = screen_dims[0]
        self.screen_height = screen_dims[1]
        self.size = random.randint(20, 80)
        self.speed = random.randint(2, 10)
        self.angle = random.random() * 2 * math.pi
        self.dir_x = math.cos(self.angle)
        self.dir_y = math.sin(self.angle)
        if self.dir_x > 0 and self.dir_y > 0:
            self.face = random.choice(['left', 'top'])
        elif self.dir_x > 0 and self.dir_y <= 0:
            self.face = random.choice(['left', 'bottom'])
        elif self.dir_x <= 0 and self.dir_y > 0:
            self.face = random.choice(['right', 'top'])
        elif self.dir_x <= 0 and self.dir_y <= 0:
            self.face = random.choice(['right', 'bottom'])
        if self.face == 'left':
            self.center = (-self.size, random.randint(0, self.screen_height - self.size))
        elif self.face == 'right':
            self.center = (self.screen_width + self.size, random.randint(0, self.screen_height - self.size))
        elif self.face == 'top':
            self.center = (random.randint(0, self.screen_width - self.size), -self.size)
        elif self.face == 'bottom':
            self.center = (random.randint(0, self.screen_width - self.size), self.screen_height)
        self.surf = pygame.image.load("./game/static/asteroid.png")
        self.surf = pygame.transform.scale(self.surf, (self.size, self.size))
        self.surf = self.surf.convert_alpha()
        self.rect = self.surf.get_rect(center=self.center)

    # Update location, kill if moved off of the screen
    def update(self):
        self.rect.move_ip(self.speed * self.dir_x, self.speed * self.dir_y)
        if self.rect.right < -50:
            self.kill()
        elif self.rect.left > self.screen_width + 50:
            self.kill()
        elif self.rect.top > self.screen_height + 50:
            self.kill()
        elif self.rect.bottom < -50:
            self.kill()
