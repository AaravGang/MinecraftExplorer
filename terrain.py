import pygame
from tile import Tile
import noise
import random
import math
from constants import *
from player import Player
from inventory import Inventory


class Terrain:
    PLAYER_REACH = 2

    def __init__(self, rows, cols, tile_size, inventory: Inventory, player_x,player_y) -> None:
        # dimensions
        self.rows, self.cols, self.tile_size = rows, cols, tile_size
        self.rows_, self.cols_ = rows+2, cols+2
        self.width, self.height = self.cols_*self.tile_size, self.rows_*self.tile_size
        self.center = (int(self.cols_//2), int(self.rows_//2))

        self.rect = pygame.Rect(-32, -32, self.width, self.height)

        # surface
        self.surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.sky_color = (177, 209, 250)

        # offsets
        self.offset = pygame.Vector2(0, 0)
        self.change = pygame.Vector2(0, 0)
        self.topleft = pygame.Vector2(0, 0)

        # grids
        self.map = [[Tile(row, col, "empty") for col in range(self.cols_)]
                    for row in range(self.rows_)]

        self.ground_level = self.rows//2  # set a ground level

        # rrow indicies of the surface tiles
        self.surface_tiles = [float("inf") for c in range(self.cols_)]

        # noise constants
        self.alt_scale = 25
        self.alt_seed = -2937  # random.randint(-10000, 10000)

        self.moisture_scale = 50
        self.moisture_seed = -242  # random.randint(-10000, 10000)

        self.cave_scale = 25
        self.cave_seed = 4620  # random.randint(-10000, 10000)
        self.cave_multiplier = 0.1

        self.alt_noise_seed = 8812  # random.randint(-10000, 10000)

        self.octaves = 5
        self.persistence = 0.5
        self.lacunarity = 2

        print(self.alt_seed, self.moisture_seed,
              self.cave_seed, self.alt_noise_seed)

        self.inventory = inventory
        self.player_x, self.player_y = player_x, player_y

        # player reach
        self.player_x_reach = (
            int((self.player_x - self.change.x)//self.tile_size - self.PLAYER_REACH), int((self.player_x - self.change.x)//self.tile_size + self.PLAYER_REACH+1))
        self.player_y_reach = (
            int((self.player_y - self.change.y)//self.tile_size - self.PLAYER_REACH), int((self.player_y - self.change.y)//self.tile_size + self.PLAYER_REACH+1))

        print(self.rows_//2, self.cols_//2,
              (self.player_x - self.change.x)//self.tile_size, (self.player_y - self.change.y)//self.tile_size)

        for r in range(*self.player_y_reach):
            for c in range(*self.player_x_reach):
                print(r, c, end=", ")
            print()

        self.highlighted = (None, None)
        self.destroyed = {}
        self.placed = {}

    # draw every tile
    # optimise later
    def draw(self, surf):

        surf.fill((0, 0, 0))
        # self.map[self.center[1]][self.center[0]].set_color((255, 0, 0))
        # self.map[int((self.player_y+self.change.y-self.rect.topleft[1])//self.tile_size+1)
        #          ][int((self.player_x-self.rect.topleft[0]+self.change.x)//self.tile_size+1)].set_color((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

        for row in range(self.rows_):
            for col in range(self.cols_):
                self.map[row][col].draw(
                    self.surf, (col)*self.tile_size, (row)*self.tile_size)

        surf.blit(self.surf, (*(self.rect.topleft - self.change),
                  self.rect.width, self.rect.height))


    def generate(self):

        # 2D: range= (-0.707,0.707)
        for col in range(self.cols_):
            terrain_height = (self.rows_-self.ground_level+int(noise.pnoise1((self.offset.x+col)/self.alt_scale,
                                                                             octaves=self.octaves,
                                                                             persistence=self.persistence,
                                                                             lacunarity=self.lacunarity,

                                                                             base=self.alt_seed)*self.rows_))/self.rows_

            cave_height = ((self.rows_-self.ground_level+abs(noise.pnoise1((self.offset.x+col)/150,
                                                                           octaves=4,
                                                                           persistence=0.5,
                                                                           lacunarity=2,

                                                                           base=self.cave_seed)*self.rows_))/self.rows_-1)

            for row in range(self.rows_):
                self.map[row][col].set_type("empty")
                key = (self.offset.y+row, self.offset.x+col)

                if key in self.destroyed:
                    self.map[row][col].set_type(
                        self.destroyed[key]["type"], self.destroyed[key]["cave"])

                    self.destroy(row, col, force=True)
                    # self.map[row][col].destroy(force=True)

                    continue

                elif key in self.placed:
                    self.map[row][col].set_type(
                        self.placed[key])
                    continue

                # normalize to range of [0,1]
                moisture = abs(noise.snoise2(key[1]/self.moisture_scale,
                                             key[0]/self.moisture_scale,
                                             octaves=self.octaves,
                                             persistence=self.persistence,
                                             lacunarity=self.lacunarity,
                                             base=self.moisture_seed)*1.4)

                # some error added to terrain_height, so that the transition between biomes is not super obvious
                n = abs(noise.snoise2(key[1]/self.alt_scale, key[0]/self.alt_scale,
                        octaves=self.octaves, persistence=self.persistence, lacunarity=self.lacunarity, base=self.alt_noise_seed))*1.4*0.3

                # normlise the current row+offset to [0,1]
                alt = (self.rows_-key[0])/self.rows_

                # below surface
                if alt < terrain_height:

                    # add the error
                    alt_ = alt+n

                    # if the altitude is above the netherite height
                    if alt > cave_height:
                        # snow
                        if moisture >= 0.5 and alt_ >= 0.7:
                            self.map[row][col].set_type("ice")

                        # water
                        elif moisture >= 0.5 and 0.7 >= alt_ >= 0.4:
                            self.map[row][col].set_type("snow")

                        # marsh
                        elif 0.3 <= moisture <= 0.5 and alt_ >= 0.5:
                            self.map[row][col].set_type("marsh")

                        # jungle
                        elif 0.3 <= moisture <= 0.5 and 0.5 >= alt_ >= 0.2:
                            self.map[row][col].set_type("jungle")

                        # desert
                        elif 0 <= moisture <= 0.1 and 0.4 >= alt_ >= 0.2:
                            self.map[row][col].set_type("desert")

                        # mountain
                        elif 0 <= moisture <= 0.3 and alt_ >= 0.5:
                            self.map[row][col].set_type("mountain")

                        # gravel
                        elif 0 <= moisture <= 0.3 and 0.2 >= alt_ >= 0:
                            self.map[row][col].set_type("gravel")

                        # dirt
                        else:
                            self.map[row][col].set_type("dirt")

                    # in the cave
                    else:
                        # add unbreakable netherite
                        if alt >= cave_height-0.1:
                            # add portal
                            if (self.offset.x+col) % (2*self.rows_+7) <= 2:
                                self.map[row][col].set_type("portal")

                            else:
                                self.map[row][col].set_type("netherite")

                        # the cave
                        else:
                            # stone
                            if 0 <= moisture <= 0.3:
                                self.map[row][col].set_type("stone")

                            # bg dirt
                            else:
                                self.map[row][col].set_type("dirt")
                                self.map[row][col].hollow()

                            self.map[row][col].set_as_cave()

                # what if cave_height is above terrain_height
                # in that case to avoid making cave open to surface, add netherite
                if cave_height > terrain_height:
                    # add unbreakable netherite
                    if cave_height > alt >= terrain_height-0.1:
                        # add portal
                        if (self.offset.x+col) % (2*self.rows_+7) <= 2:
                            self.map[row][col].set_type("portal")
                        else:
                            self.map[row][col].set_type("netherite")

    def on_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:
                if self.highlighted[0]:
                    self.destroy(self.highlighted[0], self.highlighted[1])

            if event.button == 3:
                if self.highlighted[0]:
                    self.place(
                        self.highlighted[0], self.highlighted[1])

    def destroy(self, row, col, force=False):

        # if not force:
        #     # if player is above, and theres a tile in between
        #     if self.center[1] < row-1 and not self.map[row-1][col].get_empty():
        #         return False

        #     # if player is below, and theres a tile in between
        #     if self.center[1] > row+1 and not self.map[row+1][col].get_empty():
        #         return False

        #     # if player is left, and theres a tile in between
        #     if self.center[0] < col-1 and not self.map[row][col-1].get_empty():
        #         return False

        #     # if player is right, and theres a tile in between
        #     if self.center[0] > col+1 and not self.map[row][col+1].get_empty():
        #         return False

        type = self.map[row][col].type
        cave = self.map[row][col].cave
        key = (
            int(self.offset.y)+row, int(self.offset.x)+col)

        if force:
            self.map[row][col].destroy(force=True)
        else:
            if not self.map[row][col].destroy():
                return False
            self.destroyed[key] = {}
            self.destroyed[key]["type"] = type
            self.destroyed[key]["cave"] = cave
            self.inventory.add(type)
            if key in self.placed:
                self.placed.pop(key)

    def highlight_range(self):
        pass

    def place(self, row, col):
        if self.map[row][col].get_empty():
            if not self.map[row+1][col].get_empty():
                type = self.inventory.pop()
                key = (int(self.offset.y)+row, int(self.offset.x)+col)
                if not type:
                    return False
                self.placed[key] = type
                self.map[row][col].set_type(type)

                if key in self.destroyed:
                    self.destroyed.pop(key)
        return False

    def update(self, player_vel):

        x, y = pygame.mouse.get_pos()
        x -= self.rect.topleft[0] - self.change.x
        y -= self.rect.topleft[1] - self.change.y

        row, col = int(y//self.tile_size), int(x//self.tile_size)

        # unhighlight previous
        if self.highlighted[0]:

            self.map[self.highlighted[0]
                     ][self.highlighted[1]].highlight(self.map, 0)
            self.highlighted = (None, None)

        # highlight current
        if (self.in_reach(row, col)):
            self.map[row][col].highlight(self.map, 1)
            self.highlighted = (row, col)

        self.topleft += player_vel
        self.change += player_vel

        if abs(self.change.x) >= self.tile_size or abs(self.change.y) >= self.tile_size:
            self.update_terrain()

    def in_reach(self, row, col):
        pr, pc = self.get_player_rc()
        if (pc-self.PLAYER_REACH <= col <= pc+self.PLAYER_REACH and pr-self.PLAYER_REACH <= row <= pr+self.PLAYER_REACH):
            return True

        return False

    def get_player_rc(self):
        return (int((self.player_y+self.change.y-self.rect.topleft[1])//self.tile_size), int((self.player_x-self.rect.topleft[0]+self.change.x)//self.tile_size))

    def update_terrain(self):
        if abs(self.change.x) > self.tile_size:
            dir = int(self.change.x/abs(self.tile_size))
            self.change.x -= dir*self.tile_size
            self.offset.x += dir
            # self.horizontal_scroll(dir)

            # self.horizontal_scroll(self, dir)

        if abs(self.change.y) > self.tile_size:
            dir = int(self.change.y//abs(self.tile_size))
            self.change.y -= dir*self.tile_size
            self.offset.y += dir
            # self.vertical_scroll(dir)
        # self.view_noise()

        # self.view_noise()
        self.generate()
