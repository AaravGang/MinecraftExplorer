import pygame
from constants import *
w = pygame.display.set_mode((10, 10))  # set up a minimal display window


class Player(pygame.sprite.Sprite):
    LEFT_WALK = 1
    RIGHT_WALK = 3
    PLAYER_SPEED = 10
    GRAVITY = 1

    def __init__(self, x, y):
        super().__init__()
        # define player dimensions and starting position
        self.width, self.height = 30, 50
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.x, self.y = x, y

        # animation counter and surface for player representation
        self.anim_count = 0
        self.surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # initialize player velocity as a vector
        self.vel = pygame.Vector2(0, 0)
        print(self.rect)  # debug: print initial player rectangle

    # handle key events to control movement
    def on_event(self, event):
        if event.type == pygame.KEYDOWN:
            # set velocity for each arrow key press
            if event.key == pygame.K_RIGHT:
                self.vel.x = self.PLAYER_SPEED
            if event.key == pygame.K_LEFT:
                self.vel.x = -self.PLAYER_SPEED
            if event.key == pygame.K_UP:
                self.vel.y = -self.PLAYER_SPEED
            if event.key == pygame.K_DOWN:
                self.vel.y = self.PLAYER_SPEED

        # reset velocity to zero on key release
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                self.vel.x = 0
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                self.vel.y = 0

    # check for and respond to collisions with the terrain
    def update(self, terrain):
        r, c = terrain.get_player_rc()  # get player row and column in terrain grid

        # check bottom collision when moving downward
        if self.vel.y >= 0 and (
                not terrain.map[r+1][c-1].get_empty() or
                not terrain.map[r+1][c].get_empty() or
                not terrain.map[r+1][c+1].get_empty()):
            # define bottom cells: left, center, right
            bl, bc, br = terrain.map[r+1][c -
                                          1], terrain.map[r+1][c], terrain.map[r+1][c+1]
            bottoms = [bl, bc, br]  # list for bottom tiles

    # render the player on the screen
    def draw(self, surf):
        self.surf.fill((255, 0, 0))  # fill surface with player color
        surf.blit(self.surf, self.rect)  # draw player on the provided surface
