import pygame
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT
)

class Player(pygame.sprite.Sprite):
    def __init__(self, screen_dims):
        super(Player, self).__init__()
        self.screen_width = screen_dims[0]
        self.screen_height = screen_dims[1]
        self.lives = 3
        self.surf = pygame.image.load("./game/static/spaceship.png")
        aspect_ratio = self.surf.get_height() / self.surf.get_width()
        scaled_height = self.screen_height * 0.05
        scaled_width = scaled_height * aspect_ratio
        self.surf = pygame.transform.scale(
            self.surf, (scaled_height, scaled_width)
        )
        self.surf = self.surf.convert_alpha()
        self.rect = self.surf.get_rect(
            center = (
                (self.screen_width + scaled_width) / 2, 
                (self.screen_height + scaled_height) / 2
            )
        )

    # Move the sprite based on user keypresses
    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -5)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, 5)
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)

        # Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.screen_width:
            self.rect.right = self.screen_width
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= self.screen_height:
            self.rect.bottom = self.screen_height

    def die(self):
        self.lives -= 1
