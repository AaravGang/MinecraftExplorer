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

        self.color = (0, 0, 0)
        self.use_color =False

        self.selected = False
        self.highlighted = False

        self.destroyed = False

    # update type
    def set_type(self, t):
        a = self.type
        self.type = t
        self.sprites = TILE_LOOKUP[t]["sprites"]
        self.bg = TILE_LOOKUP[t]["bg_sprites"]
        self.destroyed = False
        self.color = (0, 0, 0)
        self.sprite_ind = 0
        self.bg_ind = 0
        
        

    def set_color(self, color):
        self.color = color
        self.use_color = True

    def destroy(self,):
        self.destroyed = True

    # draw
    def draw(self, surf: pygame.Surface, x=None, y=None):
        if self.use_color:
            pygame.draw.rect(surf,self.color,(self.x,self.y,self.tile_size
                                              ,self.tile_size))
        elif self.type == "empty":
            pygame.draw.rect(surf, SKY_COLOR, (self.x, self.y,
                             self.tile_size, self.tile_size))
  
        elif self.destroyed:

            surf.blit(self.bg[self.bg_ind], (self.x, self.y))
        else:
            surf.blit(self.sprites[self.sprite_ind], (self.x, self.y))

        # elif self.sprite is not None:
        #     surf.blit(self.sprite, (self.x, self.y))
        # else:
        #     pygame.draw.rect(surf, (SKY_COLOR), (self.x, self.y,
        #                      self.tile_size, self.tile_size))
