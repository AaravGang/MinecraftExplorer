import pygame
from constants import *
w = pygame.display.set_mode((10, 10))


class Player(pygame.sprite.Sprite):
    LEFT_WALK = 1
    RIGHT_WALK = 3
    PLAYER_SPEED = 10
    GRAVITY = 1

    def __init__(self, x, y):
        super().__init__()
        self.width, self.height = 30, 50
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.x, self.y = x, y

        self.anim_count = 0

        self.surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.vel = pygame.Vector2(0, 0)
        print(self.rect)

    def on_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.vel.x = self.PLAYER_SPEED

            if event.key == pygame.K_LEFT:
                self.vel.x = -self.PLAYER_SPEED

            if event.key == pygame.K_UP:
                self.vel.y = -self.PLAYER_SPEED

            if event.key == pygame.K_DOWN:
                self.vel.y = self.PLAYER_SPEED

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                self.vel.x = 0

            if event.key == pygame.K_LEFT:
                self.vel.x = 0

            if event.key == pygame.K_UP:

                self.vel.y = 0

            if event.key == pygame.K_DOWN:
                self.vel.y = 0

    # collision checking
    def update(self, terrain):
        r, c = terrain.get_player_rc()
       

        # check bottom
        if self.vel.y >= 0 and (not terrain.map[r+1][c-1].get_empty() or not terrain.map[r+1][c].get_empty() or not terrain.map[r+1][c+1].get_empty()):
            bl, bc, br = terrain.map[r+1][c -
                                          1], terrain.map[r+1][c], terrain.map[r+1][c+1]
            # bottom left, center and right
            bottoms = [bl, bc, br]

    def draw(self, surf):
        self.surf.fill((255, 0, 0))
        surf.blit(self.surf, self.rect)
