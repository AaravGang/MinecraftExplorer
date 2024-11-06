import pygame
import os
from constants import *


class Tile(pygame.sprite.Sprite):

    def __init__(self, row, col, type="empty"):
        super().__init__()
        # constant
        self.row, self.col, self.tile_size = row, col, TILE_SIZE
        # where to draw
        self.x, self.y = self.col*self.tile_size, self.row*self.tile_size
        self.rect = pygame.Rect(self.x, self.y, self.tile_size, self.tile_size)

        # type of tile
        self.type = type

        # sprite blitting
        self.sprites = TILE_LOOKUP[type]["sprites"]
        self.sprite_ind = 0

        self.bg = TILE_LOOKUP[type]["bg_sprites"]
        self.bg_ind = 0

        # is it a cave
        self.cave = False

        # debug vars
        self.color = (0, 0, 0)
        self.highlight_color = (255, 255, 255)
        self.highlight_fill = (0, 0, 0, 0)
        self.use_color = False

        # tile selection
        self.selected = False
        self.highlighted = 0

        # tile props
        self.unbreakable = TILE_LOOKUP[type].get("unbreakable")
        self.hollowed = False
        self.has_bg = len(self.bg) > 0

        # tile neighbors
        self.bottom = (row+1, col)

        # pygame surfs
        self.surf = None
        self.mask = pygame.mask.from_surface(
            self.sprites[self.sprite_ind]) if len(self.sprites) > 0 else False
        self.image = None

    # if it's a tile near the player, give it a surface ( for alpha coloring )
    def make_surf(self):
        self.surf = pygame.Surface(
            (self.tile_size, self.tile_size), pygame.SRCALPHA)

    # update type
    def set_type(self, t, cave=False):

        self.type = t
        self.sprites = TILE_LOOKUP[t]["sprites"]
        self.bg = TILE_LOOKUP[t]["bg_sprites"]
        self.sprite_ind = 0
        self.bg_ind = 0
        self.unbreakable = TILE_LOOKUP[t].get("unbreakable")

        self.cave = cave
        self.hollowed = False
        self.has_bg = len(self.bg) > 0

        self.color = (0, 0, 0)
        self.use_color = False
        self.highlight_color = (255, 255, 255)
        self.highlight_fill = (0, 0, 0, 0)

        self.mask = pygame.mask.from_surface(
            self.sprites[self.sprite_ind]) if len(self.sprites) > 0 else False
        self.image = None
        if len(self.sprites) > 0:
            self.image = self.sprites[self.sprite_ind]

    # wacky higlighting ( will change )
    def highlight(self, map, h=1, color=None):
        if color:
            self.highlight_color = color
            self.highlighted = h
            return
        self.highlight_color = (255, 255, 255)
        self.highlight_fill = (0, 0, 0, 0)
        if map[self.bottom[0]][self.bottom[1]].get_empty() or not self.get_empty():
            self.highlight_color = (255, 0, 0)

        if not self.get_empty() and not self.unbreakable:
            self.highlight_fill = (255, 0, 0, 50)

        self.highlighted = h

    # get passable or not
    def get_empty(self):
        return self.type == "empty" or self.hollowed

    # debug
    def set_color(self, color):
        self.color = color
        self.use_color = True

    # destroy tile if its a normal one, if its a cave tile, hollow it
    def destroy(self, force=False):
        if (self.get_empty() or self.unbreakable) and not force:
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
        self.image = self.bg[self.bg_ind]

    
    def set_image(self):
        if self.get_empty():
            self.image = None

            return False
        self.image = self.sprites[0]
        return True

    def clear(self, surf, rect):
        surf.fill((0, 0, 0), rect)

    # draw
    def draw(self, surf: pygame.Surface, x=None, y=None):
        surf.fill((0, 0, 0), self.rect)

        if self.use_color:
            pygame.draw.rect(surf, self.color, self.rect)
        elif self.type == "empty":

            pygame.draw.rect(surf, SKY_COLOR, self.rect)

        elif self.hollowed:
            pygame.draw.rect(surf, (100, 100, 100), self.rect)

            surf.blit(self.bg[self.bg_ind], self.rect)
        else:
            surf.blit(self.sprites[self.sprite_ind], self.rect)

        if self.highlighted:
            if self.surf is not None:
                self.surf.fill(self.highlight_fill)
                surf.blit(self.surf, self.rect)

            pygame.draw.rect(surf, self.highlight_color, self.rect, 3)
