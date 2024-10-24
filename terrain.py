import pygame
from tile import Tile
import noise
import random


class Terrain:
    SPEED = 32

    def __init__(self, rows, cols, tile_size) -> None:
        # dimensions
        self.rows, self.cols, self.tile_size = rows, cols, tile_size
        self.width, self.height = self.cols*self.tile_size, self.rows*self.tile_size

        # surface
        self.surf = pygame.Surface((self.width, self.height))
        self.sky_color = (177, 209, 250)

        # offsets
        self.offset = pygame.Vector2(0, 0)
        self.change = pygame.Vector2(0, 0)

        self.topleft = pygame.Vector2(0, 0)

        self.speed = pygame.Vector2(0, 0)

        self.map = [[Tile(row, col, None) for col in range(self.cols)]
                    for row in range(self.rows)]

        self.ground_level = self.rows//24  # 8 tiles from bottom

        # store self.cols number of blocks representing the surface of the terrain
        self.surface_tiles = [float("inf") for c in range(self.cols)]

        self.alt_scale = 25
        self.alt_seed = 131  # random.randint(0, 1000)

        self.moisture_scale = 50
        self.moisture_seed = 8316  # random.randint(5000, 10000)

        self.cave_scale = 50
        self.cave_seed = 45  # random.randint(0, 100)

        print(self.alt_seed, self.moisture_seed, self.cave_seed)

        self.octaves = 5
        self.persistence = 0.5
        self.lacunarity = 2

    # draw every tile
    # optimise later

    def draw(self, surf):
        self.surf.fill(self.sky_color)

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

    def generate(self):

        for col in range(self.cols):

            # 1D: range = (-1,1)
            height_map = int(noise.pnoise1((self.offset.x+col)/self.alt_scale,
                                           octaves=self.octaves,
                                           persistence=self.persistence,
                                           lacunarity=self.lacunarity,
                                           base=self.alt_seed)*self.rows)

            # making the terrain
            for row in range(self.rows):
                tile = self.map[row][col]

                type = self.get_biome(row, col, height_map)
                tile.set_type(type)

            for row in range(self.rows):
                tile = self.map[row][col]
                tile.set_type(self.get_cave(row, col, height_map))

    # define biome type based on temp and moisture

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
            moisture = abs(noise.pnoise2((self.offset.x+col)/self.moisture_scale,
                                         (self.offset.y+row) /
                                         self.moisture_scale,
                                         octaves=self.octaves,
                                         persistence=self.persistence,
                                         lacunarity=self.lacunarity,
                                         base=self.moisture_seed))

            # decide biome
            if temp <= 0.5 and (row+self.offset.y) <= self.surface_tiles[col]+3:
                type = "snow"

            elif temp >= 0.5 and moisture >= 0.1 and row+self.offset.y <= self.surface_tiles[col]+10:
                type = "marsh"

            elif temp >= 0.8 and moisture <= 0.05:
                type = "sand"

            else:
                if (row+self.offset.y) == self.surface_tiles[col]:
                    type = "grass_dirt"
                else:
                    type = "dirt"

        return type

    def get_cave(self, row, col, height_map):
        type = self.map[row][col].type
        if self.rows-(row+self.offset.y) < self.ground_level - height_map - 8:

            cave_map = abs(noise.pnoise2((self.offset.x+col)/self.cave_scale,
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

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                self.speed.x = 0
            if event.key == pygame.K_LEFT:
                self.speed.x = 0
            if event.key == pygame.K_DOWN:
                self.speed.y = 0
            if event.key == pygame.K_UP:
                self.speed.y = 0

    def update(self):
        # print(self.offset)

        self.topleft += self.speed
        self.change += self.speed

        if abs(self.change.x) >= self.tile_size or abs(self.change.y) >= self.tile_size:
            self.update_terrain()

    def update_terrain(self):
        if abs(self.change.x) > self.tile_size:
            dir = int(self.change.x/abs(self.change.x))
            self.change.x -= dir*self.tile_size
            self.offset.x += dir
            self.horizontal_scroll(dir)

            # self.horizontal_scroll(self, dir)

        if abs(self.change.y) > self.tile_size:
            dir = int(self.change.y/abs(self.change.y))
            self.change.y -= dir*self.tile_size
            self.offset.y += dir
            self.vertical_scroll(dir)

        # self.generate()

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
