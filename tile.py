import pygame
import os
from constants import *


class Tile:

    def __init__(self, row, col, type="empty"):
        # constant
        self.row, self.col, self.tile_size = row, col, TILE_SIZE
        # where to draw
        self.x, self.y = self.col*self.tile_size, self.row*self.tile_size

        self.type = type

        self.sprites = TILE_LOOKUP[type]["sprites"]
        self.sprite_ind = 0

        self.bg = TILE_LOOKUP[type]["bg_sprites"]
        self.bg_ind = 0
        self.cave = False

        self.color = (0, 0, 0)
        self.highlight_color = (255, 255, 255)
        self.highlight_fill = (0, 0, 0, 0)
        self.use_color = False

        self.selected = False
        self.highlighted = 0
        self.player = False

        self.unbreakable = TILE_LOOKUP[type].get("unbreakable")
        self.hollowed = False
        self.has_bg = len(self.bg) > 0

        # only used by tiles near the player, so its fine if row+1 is out of range
        self.bottom = (row+1, col)
        self.surf = None

    def make_surf(self):
        self.surf = pygame.Surface(
            (self.tile_size, self.tile_size), pygame.SRCALPHA)

    # update type
    def set_type(self, t, cave=False):

        self.type = t
        self.sprites = TILE_LOOKUP[t]["sprites"]
        self.bg = TILE_LOOKUP[t]["bg_sprites"]
        self.unbreakable = TILE_LOOKUP[t].get("unbreakable")
        self.hollowed = False
        self.has_bg = len(self.bg) > 0
        self.sprite_ind = 0
        self.bg_ind = 0
        if not self.player:
            self.color = (0, 0, 0)

            self.use_color = False

        self.cave = cave
        self.highlight_color = (255, 255, 255)
        self.highlight_fill = (0, 0, 0, 0)

    def highlight(self, map, h=1):
        self.highlight_color = (255, 255, 255)
        self.highlight_fill = (0, 0, 0, 0)
        if map[self.bottom[0]][self.bottom[1]].get_empty() or not self.get_empty():
            self.highlight_color = (255, 0, 0)

        if not self.get_empty() and not self.unbreakable:
            self.highlight_fill = (255, 0, 0, 50)

        self.highlighted = h

    def get_empty(self):
        return self.type == "empty" or self.hollowed

    def make_player(self):
        self.use_color = True
        self.color = (255, 0, 0, 255)
        self.player = True

    def set_color(self, color):
        self.color = color
        self.use_color = True

    def destroy(self, center=None, map=None, force=False):
        if not force:
            # if player is above, and theres a tile in between
            if center[1] < self.row-1 and not map[self.row-1][self.col].get_empty():
                return False

            # if player is below, and theres a tile in between
            if center[1] > self.row+1 and not map[self.row+1][self.col].get_empty():
                return False

            # if player is left, and theres a tile in between
            if center[0] < self.col-1 and not map[self.row][self.col-1].get_empty():
                return False

            # if player is right, and theres a tile in between
            if center[0] > self.col+1 and not map[self.row][self.col+1].get_empty():
                return False

        if self.get_empty() or self.unbreakable:
            return False
        elif self.cave:
            self.hollow()
        else:
            self.set_type("empty")

        return True

    def set_as_cave(self):
        self.cave = True

    def hollow(self):
        self.hollowed = True

    # draw

    def draw(self, surf: pygame.Surface, x=None, y=None):
        surf.fill((0, 0, 0), (self.x, self.y, self.tile_size, self.tile_size))

        if self.use_color:
            pygame.draw.rect(surf, self.color, (self.x, self.y,
                             self.tile_size, self.tile_size))
        elif self.type == "empty":

            pygame.draw.rect(surf, SKY_COLOR, (self.x, self.y,
                             self.tile_size, self.tile_size))

        elif self.hollowed:
            pygame.draw.rect(surf, (100, 100, 100), (self.x, self.y,
                             self.tile_size, self.tile_size))

            surf.blit(self.bg[self.bg_ind], (self.x, self.y))
        else:
            surf.blit(self.sprites[self.sprite_ind], (self.x, self.y))

        if self.highlighted:
            if self.surf is not None:
                self.surf.fill(self.highlight_fill)
                surf.blit(self.surf, (self.x, self.y))

            pygame.draw.rect(surf, self.highlight_color, (self.x, self.y,
                             self.tile_size, self.tile_size), 3)
