from terrain import Terrain
from inventory import Inventory
from player import Player

import pygame
import os
from constants import *
pygame.display.init()

WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA)
clock = pygame.time.Clock()
FPS = 30


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


def draw(terrain: Terrain, inventory: Inventory, player: Player):

    terrain.draw(WIN)
    inventory.draw(WIN)
    player.draw(WIN)
    pygame.display.update()


def main():
    run = True

    load_tiles()

    # terrain.view_noise()
    inventory = Inventory(9, 10, 2*TILE_SIZE,
                          2 * TILE_SIZE, TILE_SIZE)
    px, py = (WIDTH+TILE_SIZE*2)//2-15, (HEIGHT+TILE_SIZE*2)//2-25
    player = Player(px, py)
    terrain = Terrain(ROWS, COLS, TILE_SIZE, inventory, px, py)

    terrain.generate()

    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                terrain.on_event(event)
                player.on_event(event)

            if event.type == pygame.KEYUP:
                terrain.on_event(event)
                player.on_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                terrain.on_event(event)
                inventory.on_event(event)

        player.update(terrain)
        draw(terrain, inventory, player)
        terrain.update(player.vel)
        inventory.update()


if __name__ == "__main__":
    main()
