import pygame
from tile import Tile
import noise
import random
import math
from constants import *


class Terrain:
    SPEED = 1000
    PLAYER_REACH = 2

    def __init__(self, rows, cols, tile_size, inventory) -> None:
        # dimensions
        self.rows, self.cols, self.tile_size = rows, cols, tile_size
        self.width, self.height = self.cols*self.tile_size, self.rows*self.tile_size
        self.center = (int(self.cols//2), int(self.rows//2))

        # surface
        self.surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.sky_color = (177, 209, 250)

        # offsets
        self.offset = pygame.Vector2(0, 0)
        self.change = pygame.Vector2(0, 0)
        self.topleft = pygame.Vector2(0, 0)

        self.speed = pygame.Vector2(0, 0)

        # grids
        self.map = [[Tile(row, col, "empty") for col in range(self.cols)]
                    for row in range(self.rows)]

        self.ground_level = self.rows//2  # set a ground level

        # rrow indicies of the surface tiles
        self.surface_tiles = [float("inf") for c in range(self.cols)]

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

        # player reach
        self.player_x_reach = (
            int(self.center[0] - self.PLAYER_REACH), int(self.center[0]+self.PLAYER_REACH+1))
        self.player_y_reach = (
            int(self.center[1]-self.PLAYER_REACH), int(self.center[1]+self.PLAYER_REACH+1))
        self.player_reach = []
        [[self.player_reach.append(self.map[r][c]) or self.map[r][c].make_surf() for c in range(*self.player_x_reach)]
         for r in range(*self.player_y_reach)]

        self.highlighted = (None, None)
        self.destroyed = {}
        self.placed = {}

        self.map[self.center[1]][self.center[0]].make_player()

        self.inventory = inventory

    # draw every tile
    # optimise later

    def draw(self, surf):
        for row in range(self.rows):
            for col in range(self.cols):
                self.map[row][col].draw(
                    self.surf, col*self.tile_size, row*self.tile_size)

        # for col, s in enumerate(self.surface_tiles):
        #     y = (s-self.offset.y)*self.tile_size
        #     x = (col)*self.tile_size
        #     pygame.draw.rect(self.surf, (255, 255, 255),
        #                      (x, y, self.tile_size, self.tile_size), 3)

        surf.blit(self.surf, (0, 0))

    """
    1) Get height map using !D perlin noise -> this is used to create the surface of the terrrain.
    2) Set temp = 1 - alt (temp is inversely proportional to alt)
    3) Use 2D perlin noise to get moisture.
    4) According to moisture and temp values,( somehow make sure both are -1 to 1 ) set biome
    5) generate caves, such that its atleast min_cave_depth below the terrain surface

    """

    def view_noise(self):
        # 2D: range= (-0.707,0.707)
        for col in range(self.cols):
            terrain_height = (self.rows-self.ground_level+int(noise.pnoise1((self.offset.x+col)/self.alt_scale,
                                                                            octaves=self.octaves,
                                                                            persistence=self.persistence,
                                                                            lacunarity=self.lacunarity,

                                                                            base=self.alt_seed)*self.rows))/self.rows

            cave_height = ((self.rows-self.ground_level+abs(noise.pnoise1((self.offset.x+col)/150,
                                                                          octaves=4,
                                                                          persistence=0.5,
                                                                          lacunarity=2,

                                                                          base=self.cave_seed)*self.rows))/self.rows-0.5)

            for row in range(self.rows):

                # normalize to range of [0,1]
                moisture = abs(noise.snoise2((self.offset.x+col)/self.moisture_scale,
                                             (self.offset.y+row) /
                                             self.moisture_scale,
                                             octaves=self.octaves,
                                             persistence=self.persistence,
                                             lacunarity=self.lacunarity,
                                             base=self.moisture_seed)*1.4)

                # some error added to terrain_height, so that the transition between biomes is not super obvious
                # abs(noise.snoise2((self.offset.x+col)/self.alt_scale, (self.offset.y+row)/self.alt_scale,
                n = 0
                # octaves=self.octaves, persistence=self.persistence, lacunarity=self.lacunarity, base=self.alt_noise_seed))*1.4*0.3

                # normlise the current row+offset to [0,1]
                alt = (self.rows-(self.offset.y+row))/self.rows

                self.map[row][col].set_color((0, 0, 0))

                # below surface
                if alt < terrain_height:
                    self.map[row][col].set_color([min(moisture*255, 255)]*3)

                    # add the error
                    alt_ = alt+n

                    # if the altitude is above the netherite height
                    if alt > cave_height:
                        # snow
                        if moisture >= 0.5 and alt_ >= 0.6:
                            self.map[row][col].set_color((236, 255, 253))

                        # water
                        elif moisture >= 0.5 and 0.6 >= alt_ >= 0.4:
                            self.map[row][col].set_color((35, 137, 218))

                        # marsh
                        elif 0.3 <= moisture <= 0.5 and alt_ >= 0.5:
                            self.map[row][col].set_color((139, 169, 143))

                        # jungle
                        elif 0.3 <= moisture <= 0.5 and 0.5 >= alt_ >= 0.2:
                            self.map[row][col].set_color((60, 200, 100))

                        # desert
                        elif 0 <= moisture <= 0.1 and 0.4 >= alt_ >= 0.2:
                            self.map[row][col].set_color((234, 208, 168))

                        # mountain
                        elif 0 <= moisture <= 0.3 and alt_ >= 0.5:
                            self.map[row][col].set_color((58, 50, 50))

                        # dirt
                        else:
                            self.map[row][col].set_color((118, 85, 43))

                    # in the cave
                    else:
                        # add unbreakable netherite
                        if alt >= cave_height-0.1:
                            # add portal
                            if (self.offset.x+col) % (2*self.rows+7) <= 2:
                                self.map[row][col].set_color((227, 212, 209))
                            else:
                                self.map[row][col].set_color((68, 58, 59))

                        # the cave
                        else:
                            # gravel
                            if 0 <= moisture <= moisture <= 0.3:
                                self.map[row][col].set_color((60, 70, 80))

                            # bg dirt
                            else:
                                self.map[row][col].set_color((55, 44, 11))

    def generate(self):

        # 2D: range= (-0.707,0.707)
        for col in range(self.cols):
            terrain_height = (self.rows-self.ground_level+int(noise.pnoise1((self.offset.x+col)/self.alt_scale,
                                                                            octaves=self.octaves,
                                                                            persistence=self.persistence,
                                                                            lacunarity=self.lacunarity,

                                                                            base=self.alt_seed)*self.rows))/self.rows

            cave_height = ((self.rows-self.ground_level+abs(noise.pnoise1((self.offset.x+col)/150,
                                                                          octaves=4,
                                                                          persistence=0.5,
                                                                          lacunarity=2,

                                                                          base=self.cave_seed)*self.rows))/self.rows-1)

            for row in range(self.rows):
                self.map[row][col].set_type("empty")
                key = (self.offset.y+row, self.offset.x+col)

                if key in self.destroyed:
                    self.map[row][col].set_type(
                        self.destroyed[key]["type"], self.destroyed[key]["cave"])

                    self.map[row][col].destroy(force=True)

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
                alt = (self.rows-key[0])/self.rows

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
                            if (self.offset.x+col) % (2*self.rows+7) <= 2:
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
                        if (self.offset.x+col) % (2*self.rows+7) <= 2:
                            self.map[row][col].set_type("portal")
                        else:
                            self.map[row][col].set_type("netherite")

  #  define biome type based on temp and moisture

    def get_biome(self, row, col, height_map):
        tile = self.map[row][col]
        type = "empty"

        if self.rows-(row+self.offset.y) < self.ground_level - height_map:
            if row+self.offset.y < self.surface_tiles[col]:
                self.surface_tiles[col] = row+self.offset.y

            # set temp as inv. prop. to alt
            temp = (self.rows-self.ground_level +
                    height_map)/self.rows
            # 2D: range= (-0.707,0.707)
            moisture = abs(noise.snoise2((self.offset.x+col)/self.moisture_scale,
                                         (self.offset.y+row) /
                                         self.moisture_scale,
                                         octaves=self.octaves,
                                         persistence=self.persistence,
                                         lacunarity=self.lacunarity,
                                         base=self.moisture_seed))

            # decide biome
            if moisture >= 0.7:
                if temp <= 0.3:
                    type = "snow"
                elif temp <= 0.4 and moisture >= 0.9:
                    type = "water"
                else:
                    type = "marsh"
            elif moisture <= 0.2 and temp >= 0.7:
                type = "sand"

            else:
                if (row-self.offset.y) == self.surface_tiles[col]:
                    type = "grass_dirt"
                else:
                    type = "dirt"

        return type

    def get_cave(self, row, col, height_map):
        type = self.map[row][col].type
        if self.rows-(row+self.offset.y) < self.ground_level - height_map - 8:

            cave_map = abs(noise.snoise2((self.offset.x+col)/self.cave_scale,
                                         (self.offset.y+row) / self.cave_scale,
                                         octaves=self.octaves,
                                         persistence=self.persistence,
                                         lacunarity=self.lacunarity,
                                         base=self.cave_seed))*2

            if cave_map >= 0.15:
                type = "gravel"

            if self.rows-(row+self.offset.y) >= self.ground_level - height_map - 15:
                type = "gravel"

        return type

    def on_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.speed.x = self.SPEED
            if event.key == pygame.K_LEFT:
                self.speed.x = -self.SPEED

            if event.key == pygame.K_DOWN:
                self.speed.y = self.SPEED

            if event.key == pygame.K_UP:
                self.speed.y = -self.SPEED

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                self.speed.x = 0
            if event.key == pygame.K_LEFT:
                self.speed.x = 0
            if event.key == pygame.K_DOWN:
                self.speed.y = 0
            if event.key == pygame.K_UP:
                self.speed.y = 0

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:
                if self.highlighted[0]:
                    self.destroy(self.highlighted[0], self.highlighted[1])

            if event.button == 3:
                if self.highlighted[0]:
                    self.place(
                        self.highlighted[0], self.highlighted[1])

    def destroy(self, row, col):
        type = self.map[row][col].type
        cave = self.map[row][col].cave
        key = (
            int(self.offset.y)+row, int(self.offset.x)+col)

        if self.map[row][col].destroy(self.center, self.map):
            self.destroyed[key] = {}
            self.destroyed[key]["type"] = type
            self.destroyed[key]["cave"] = cave
            self.inventory.add(type)
            if key in self.placed:
                self.placed.pop(key)

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

    def update(self):

        self.topleft += self.speed
        self.change += self.speed

        if abs(self.change.x) >= self.tile_size or abs(self.change.y) >= self.tile_size:
            self.update_terrain()

        x, y = pygame.mouse.get_pos()
        row, col = y//self.tile_size, x//self.tile_size

        # unhighlight previous
        if self.highlighted[0]:

            self.map[self.highlighted[0]
                     ][self.highlighted[1]].highlight(self.map, 0)
            self.highlighted = (None, None)

        # highlight current
        if (self.in_reach(row, col)):
            self.map[row][col].highlight(self.map, 1)
            self.highlighted = (row, col)

    def in_reach(self, row, col):
        if (self.player_x_reach[0] <= col < self.player_x_reach[1] and self.player_y_reach[0] <= row < self.player_y_reach[1]):
            return True

        return False

    def update_terrain(self):
        if abs(self.change.x) > self.tile_size:
            dir = int(self.change.x/abs(self.change.x))
            self.change.x -= dir*self.tile_size
            self.offset.x += dir
            # self.horizontal_scroll(dir)

            # self.horizontal_scroll(self, dir)

        if abs(self.change.y) > self.tile_size:
            dir = int(self.change.y/abs(self.change.y))
            self.change.y -= dir*self.tile_size
            self.offset.y += dir
            # self.vertical_scroll(dir)
        # self.view_noise()

        # self.view_noise()
        self.generate()

    def horizontal_scroll(self, dir):

        if dir > 0:
            remove = 0
            add = self.cols-1

        else:
            remove = self.cols-1
            add = 0

        self.surface_tiles.pop(remove)
        self.surface_tiles.insert(add, float("inf"))

        # remove first col
        for row in range(self.rows):
            tile = self.map[row].pop(remove)
            self.map[row].insert(add, tile)

        # generate terrain for last col
        # 1D: range = (-1,1)
        height_map = int(noise.pnoise1((self.offset.x+add)/self.alt_scale,
                                       octaves=self.octaves,
                                       persistence=self.persistence,
                                       lacunarity=self.lacunarity,
                                       base=self.alt_seed)*self.rows)

        for row in range(self.rows):

            tile = self.map[row][add]
            tile.set_type(self.get_biome(row, add, height_map))

        for row in range(self.rows):
            tile = self.map[row][add]
            tile.set_type(self.get_cave(row, add, height_map))

    def vertical_scroll(self, dir):

        if dir > 0:
            remove = 0
            add = self.rows-1
        else:
            remove = self.rows-1
            add = 0

        row = self.map.pop(remove)
        # if dir > 0:
        #     self.map.append(row)
        # else:
        self.map.insert(add, row)

        # remove first col
        for col in range(self.cols):

            # generate terrain for last col
            # 1D: range = (-1,1)
            height_map = int(noise.pnoise1((self.offset.x+col)/self.alt_scale,
                                           octaves=self.octaves,
                                           persistence=self.persistence,
                                           lacunarity=self.lacunarity,
                                           base=self.alt_seed)*self.rows)

            tile = self.map[add][col]
            tile.set_type(self.get_biome(add, col, height_map))

        # remove first col
        for col in range(self.cols):

            # generate terrain for last col
            # 1D: range = (-1,1)
            height_map = int(noise.pnoise1((self.offset.x+col)/self.alt_scale,
                                           octaves=self.octaves,
                                           persistence=self.persistence,
                                           lacunarity=self.lacunarity,
                                           base=self.alt_seed)*self.rows)

            tile = self.map[add][col]
            tile.set_type(self.get_cave(add, col, height_map))
