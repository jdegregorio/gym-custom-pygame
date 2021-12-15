# Standard imports
import math

# 3rd party imports
import pygame
import numpy as np


class Beam(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, step, max_radius, screen_size):
        super(Beam, self).__init__()
        self.x_init = x
        self.y_init = y
        self.x = x
        self.y = y
        self.radius = 0
        self.angle = angle
        self.collide = 0
        self.step = step
        self.color_rock = (255, 211, 0)
        self.color_wall = (102, 255, 0)
        self.screen_size = screen_size
        self.max_radius = max_radius
        self.surf_size = 5
        self.surf = pygame.Surface((self.surf_size, self.surf_size))
        self.rect = self.surf.get_rect(center = (x, y))

    # Iteratively step beam outward until collision or off-screen
    def beam_out(self, collide_sprites):
        done = False
        collision = False
        while not done:
            self.step_out()
            for sprite in collide_sprites:
                if sprite.rect.collidepoint(self.x, self.y):
                    collision = True
                    break
            if collision:
                self.surf.fill(self.color_rock)
                self.collide = 1
                done = True
            elif math.sqrt((self.x - self.x_init)**2 + (self.y - self.y_init)**2) > self.max_radius:
                self.x = self.x_init + math.cos(self.angle) * self.max_radius
                self.y = self.y_init + math.sin(self.angle) * self.max_radius
                self.surf.fill(self.color_wall)
                done = True
            elif self.x < 0:
                self.x = 0
                self.rect.left = 0
                self.surf.fill(self.color_wall)
                done = True
            elif self.x > self.screen_size:
                self.x = self.screen_size
                self.rect.right = self.screen_size
                self.surf.fill(self.color_wall)
                done = True
            elif self.y < 0:
                self.y = 0
                self.rect.top = 0
                self.surf.fill(self.color_wall)
                done = True
            elif self.y > self.screen_size:
                self.y = self.screen_size
                self.rect.bottom = self.screen_size
                self.surf.fill(self.color_wall)
                done = True

    # Move lidar beam outward one step
    def step_out(self):
        self.x += self.step * math.cos(self.angle)
        self.y += self.step * math.sin(self.angle)
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        self.radius = math.sqrt((self.x - self.x_init)**2 + (self.y - self.y_init)**2)

    def get_state(self):
        return (self.radius, self.collide)


class Lidar:
    def __init__(self, x, y, n_beams, step, max_radius, screen_size):
        self.x = x
        self.y = y
        self.n_beams = n_beams
        self.step = step
        self.max_radius = max_radius
        self.screen_size = screen_size
        self.angles = np.linspace(0, 2* math.pi, num=n_beams, endpoint=False)

    def sync_position(self, sprite):
        self.x = sprite.rect.centerx
        self.y = sprite.rect.centery

    def scan(self, collide_sprites):

        # Send out beams
        self.ls_beams = []
        for angle in self.angles:
            beam = Beam(
                x=self.x,
                y=self.y,
                angle=angle,
                step=self.step,
                max_radius=self.max_radius,
                screen_size=self.screen_size
            )
            self.ls_beams.append(beam)
        for beam in self.ls_beams:
            beam.beam_out(
                collide_sprites
            )

        # Summarize state
        ls_radius = []
        ls_collide = []
        for beam in self.ls_beams:
            radius, collide = beam.get_state()
            ls_radius.append(radius)
            ls_collide.append(collide)

        return ls_radius, ls_collide

    def get_beams(self):
        return self.ls_beams
