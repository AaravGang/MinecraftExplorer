from terrain import Terrain
import pygame
import os
from constants import *
pygame.display.init()

WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA)


def load_tiles():
    for type in TILE_LOOKUP:
        path = os.path.join("assets", "sprites", f"{type}.png")
        try:
            if type == "empty":
                continue
            if type.startswith("bg_"):
                img = pygame.transform.scale(pygame.image.load(
                    path), (TILE_SIZE, TILE_SIZE)).convert_alpha()
                TILE_LOOKUP[type[3:]]["bg_sprites"].append(img)
            else:
                img = pygame.transform.scale(pygame.image.load(
                    path), (TILE_SIZE, TILE_SIZE)).convert_alpha()
                TILE_LOOKUP[type]["sprites"].append(img)
        except Exception as e:
            print(e)


def draw(terrain: Terrain):
    terrain.draw(WIN)
    pygame.display.update()


def main():
    run = True

    load_tiles()
    print(TILE_LOOKUP)
    terrain = Terrain(ROWS, COLS, TILE_SIZE)
    # terrain.view_noise()

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

            if event.type == pygame.MOUSEBUTTONDOWN:
                terrain.on_event(event)
        draw(terrain)
        terrain.update()


if __name__ == "__main__":
    main()
