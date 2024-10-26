import pygame
from tile import Tile
import noise
import random


class Terrain:
    SPEED = 10

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

        self.ground_level = 15  # 8 tiles from bottom

        # store self.cols number of blocks representing the surface of the terrain
        self.surface_tiles = []

        self.alt_scale = 15
        self.alt_seed = random.randint(0, 10000)

        self.moisture_scale = 100
        self.moisture_seed = random.randint(0, 10000)

        self.octaves = 6
        self.persistence = 1
        self.lacunarity = 0.5

    # draw every tile
    # optimise later

    def draw(self, surf):
        self.surf.fill(self.sky_color)

        for layer in self.map:
            for tile in layer:
                tile.draw(self.surf)

        surf.blit(self.surf, (0, 0))

    """
    1) Get height map using !D perlin noise -> this is used to create the surface of the terrrain.
    2) Set temp = 1 - alt (temp is inversely proportional to alt)
    3) Use 2D perlin noise to get moisture.
    4) According to moisture and temp values,( somehow make sure both are -1 to 1 ) set biome
    5) generate caves, such that its atleast min_cave_depth below the terrain surface
    
    """

    def generate(self):
        self.map = [[Tile(row, col, None) for col in range(self.cols)]
                    for row in range(self.rows)]

        for col in range(self.cols):

            # 1D: range = (-1,1)
            height_map = noise.pnoise1((self.offset.x+col)/self.alt_scale,
                                       octaves=self.octaves,
                                       persistence=self.persistence,
                                       lacunarity=self.lacunarity,
                                       repeat=9999,
                                       base=self.alt_seed)
            flag = 0
            for row in range(self.rows):

                tile = self.map[row][col]
                if self.rows-(row+self.offset.y) < self.ground_level - height_map*self.rows:
                    if not flag:
                        self.surface_tiles.append(tile)
                        flag = 1

                    # set temp as inv. prop. to alt
                    temp = (self.rows-self.ground_level +
                            height_map*self.rows)/self.rows
                    # 2D: range= (-0.707,0.707)
                    moisture = abs(noise.pnoise2((self.offset.x+col)/self.moisture_scale,
                                                 (self.offset.y+row) /
                                                 self.moisture_scale,
                                                 octaves=self.octaves,
                                                 persistence=self.persistence,
                                                 lacunarity=self.lacunarity,
                                                 base=self.moisture_seed))

                    tile.set_type(self.get_type(temp, moisture))

    # define biome type based on temp and moisture

    def get_type(self, temp, moisture):
        if temp <= 0.5 and moisture >= 0.5:
            return "snow_dirt"
        elif temp >= 0.5 and moisture >= 0.5:
            return "jungle"
        elif temp >= 0.8 and moisture <= 0.2:
            return "sand"
        else:
            return "dirt"

        return "empty"

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

        self.topleft += self.speed
        self.change += self.speed

        if abs(self.change.x) >= self.tile_size or abs(self.change.y) >= self.tile_size:
            self.update_terrain()

    def update_terrain(self):
        if abs(self.change.x) > self.tile_size:
            dir = int(self.change.x/abs(self.change.x))
            self.change.x -= dir*self.tile_size
            self.offset.x += dir

        if abs(self.change.y) > self.tile_size:
            dir = int(self.change.y/abs(self.change.y))
            self.change.y -= dir*self.tile_size
            self.offset.y += dir

        self.generate()
