from terrain import Terrain
import pygame
import os
from constants import *
pygame.display.init()

WIN = pygame.display.set_mode((WIDTH, HEIGHT))


def load_tiles():
    for type in TILE_LOOKUP:
        path = os.path.join("assets", "sprites", f"{type}.png")
        try:
            img = pygame.transform.scale(pygame.image.load(
                path), (TILE_SIZE, TILE_SIZE)).convert_alpha()
            TILE_LOOKUP[type]["sprite"] = img
        except:
            TILE_LOOKUP[type]["sprite"] = None


def draw(terrain: Terrain):
    terrain.draw(WIN)
    pygame.display.update()


def main():
    run = True

    load_tiles()
    terrain = Terrain(ROWS, COLS, TILE_SIZE)
    terrain.generate()

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            elif event.type == pygame.KEYDOWN:
                terrain.on_event(event)

            elif event.type == pygame.KEYUP:
                terrain.on_event(event)

        terrain.update()
        draw(terrain)


if __name__ == "__main__":
    main()
