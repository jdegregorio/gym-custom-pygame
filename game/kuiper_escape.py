"""
Kuiper Escape

A game developed in the pygame framework. The objective is to avoid the 
asteroids/rocks for as long as possible while the rate of rocks increases 
steadily over time.

"""
import pygame
import random
import math
from player import Player
from rock import Rock

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    QUIT
)

# Define constants for the screen width and height
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
SCREEN_DIMS = (SCREEN_WIDTH, SCREEN_HEIGHT)
RATE_START = 2  # Number of rocks/second generated
RATE_INCREMENT = 50  # Add additional rock/second every N seconds

# Initialize pygame
pygame.init()
font = pygame.font.SysFont("monospace", 36)
score = 0
screen = pygame.display.set_mode(SCREEN_DIMS)
clock = pygame.time.Clock()
framerate = 50

# Instantiate player and sprite groups
player = Player(screen_dims=SCREEN_DIMS)
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
        new_rock = Rock(screen_dims=SCREEN_DIMS)
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
