"""
Rocks

Rules:
  - Single player
  - 3 lives
  - Move around using up/down/left/right arrows
  
Objectives:
  - Avoid rocks for as long as possible
"""


# Import the pygame module
import pygame
import random
import math

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

# Define constants for the screen width and height
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
PLAYER_SPEED = 5
RATE_START = 2  # Number of rocks/second generated
RATE_INCREMENT = 50  # Add additional rock/second every N seconds

# Define a player object by extending pygame.sprite.Sprite
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.lives = 3
        self.surf = pygame.image.load("static/spaceship.png")
        aspect_ratio = self.surf.get_height() / self.surf.get_width()
        scaled_height = SCREEN_HEIGHT * 0.05
        scaled_width = scaled_height * aspect_ratio
        self.surf = pygame.transform.scale(
            self.surf, (scaled_height, scaled_width)
        )
        self.surf = self.surf.convert_alpha()
        self.rect = self.surf.get_rect(
            center = (
                (SCREEN_WIDTH + scaled_width) / 2, 
                (SCREEN_HEIGHT + scaled_height) / 2
            )
        )

    # Move the sprite based on user keypresses
    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -PLAYER_SPEED)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, PLAYER_SPEED)
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-PLAYER_SPEED, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(PLAYER_SPEED, 0)

        # Keep player on the screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

    def die(self):
        self.lives -= 1


# Define the enemy object by extending pygame.sprite.Sprite
class Rock(pygame.sprite.Sprite):
    def __init__(self):
        super(Rock, self).__init__()
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
            self.center = (-self.size, random.randint(0, SCREEN_HEIGHT - self.size))
        elif self.face == 'right':
            self.center = (SCREEN_WIDTH + self.size, random.randint(0, SCREEN_HEIGHT - self.size))
        elif self.face == 'top':
            self.center = (random.randint(0, SCREEN_WIDTH - self.size), -self.size)
        elif self.face == 'bottom':
            self.center = (random.randint(0, SCREEN_WIDTH - self.size), SCREEN_HEIGHT)
        self.surf = pygame.image.load("static/asteroid.png")
        self.surf = pygame.transform.scale(self.surf, (self.size, self.size))
        self.surf = self.surf.convert_alpha()
        self.rect = self.surf.get_rect(center=self.center)

    # Update location, kill if moved off of the screen
    def update(self):
        self.rect.move_ip(self.speed * self.dir_x, self.speed * self.dir_y)
        if self.rect.right < -50:
            self.kill()
        elif self.rect.left > SCREEN_WIDTH + 50:
            self.kill()
        elif self.rect.top > SCREEN_HEIGHT + 50:
            self.kill()
        elif self.rect.bottom < -50:
            self.kill()


# Initialize pygame
pygame.init()
font = pygame.font.SysFont("monospace", 36)
score = 0
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
framerate = 50

# Instantiate player and sprite groups
player = Player()
rocks = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

# Variable to keep the main loop running
running = True

# Main loop
while running:
    # Loop through event queue
    for event in pygame.event.get():
        # Check for KEYDOWN event
        if event.type == KEYDOWN:
            # If the Esc key is pressed, then exit the main loop
            if event.key == K_ESCAPE:
                running = False
        # Check for QUIT event. If QUIT, then set running to false.
        elif event.type == QUIT:
            running = False

    # Add rocks, increase rate over time
    thres  = (1 / framerate) * (RATE_START + score/RATE_INCREMENT)
    if random.random() < thres:
        new_rock = Rock()
        rocks.add(new_rock)
        all_sprites.add(new_rock)

    # Update sprite positions
    pressed_keys = pygame.key.get_pressed()
    player.update(pressed_keys)
    rocks.update()

    # Redraw screen
    screen.fill((0, 0, 0))
    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)

    # Check for collisions, deduct player life
    collisions = pygame.sprite.spritecollide(player, rocks, dokill=False)
    for rock in collisions:
        rock.kill()
        player.die()

    # Check if player has any remaining lives
    if player.lives == 0:
        running = False

    # Update score
    score += 1 / framerate
    score_board = font.render("Score = " + str(math.floor(score)), 1, (255, 255, 255))
    lives_remaining = font.render("Lives =  " + str(player.lives), 1, (255, 255, 255))
    screen.blit(score_board, (5, 10))
    screen.blit(lives_remaining, (SCREEN_WIDTH - 200, 10))

    # Update the display
    pygame.display.flip()

    # Set framerate
    clock.tick(framerate)
