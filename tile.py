import pygame
import os
from constants import *


class Tile:

    def __init__(self, row, col, type=None):
        # constant
        self.row, self.col, self.tile_size = row, col, TILE_SIZE
        # where to draw
        self.x, self.y = self.col*self.tile_size, self.row*self.tile_size

        self.type = type
        self.sprite = TILE_LOOKUP[type]["sprite"] if type else None

    # update type
    def set_type(self, type):
        self.type = type
        self.sprite = TILE_LOOKUP[type]["sprite"]

    # draw
    def draw(self, surf, x=None, y=None):
        if x is not None and y is not None:
            self.x, self.y = x, y
        if self.sprite is not None:
            surf.blit(self.sprite, (self.x, self.y))
        else:
            pygame.draw.rect(surf, (SKY_COLOR), (self.x, self.y,
                             self.tile_size, self.tile_size))
