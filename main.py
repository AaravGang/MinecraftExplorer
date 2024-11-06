from terrain import Terrain
from inventory import Inventory
from player import Player

# main libraries and constants for game functionality
import pygame
import os
from constants import *

pygame.display.init()  # initialize display

# set up main game window and frame rate
WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA)
clock = pygame.time.Clock()
FPS = 30

# load tiles for different game objects


def load_tiles():
    for type in TILE_LOOKUP:
        path = os.path.join("assets", "sprites", f"{type}.png")
        try:
            # skip loading for empty tiles
            if type == "empty":
                continue
            # process background and regular tiles differently
            if type.startswith("bg_"):
                img = pygame.transform.scale(pygame.image.load(
                    path), (TILE_SIZE, TILE_SIZE)).convert_alpha()
                TILE_LOOKUP[type[3:]]["bg_sprites"].append(img)
            else:
                img = pygame.transform.scale(pygame.image.load(
                    path), (TILE_SIZE, TILE_SIZE)).convert_alpha()
                TILE_LOOKUP[type]["sprites"].append(img)
        except Exception as e:
            print(e)  # handle loading errors

# draw main game components on the window


def draw(terrain: Terrain, inventory: Inventory, player: Player):
    terrain.draw(WIN)
    inventory.draw(WIN)
    player.draw(WIN)
    pygame.display.update()

# main game loop


def main():
    run = True

    load_tiles()  # load all tiles at the start

    # initialize inventory, player, and terrain with specified parameters
    inventory = Inventory(9, 10, 2 * TILE_SIZE, 2 * TILE_SIZE, TILE_SIZE)
    px, py = (WIDTH + TILE_SIZE * 2) // 2 - \
        15, (HEIGHT + TILE_SIZE * 2) // 2 - 25
    player = Player(px, py)
    terrain = Terrain(ROWS, COLS, TILE_SIZE, inventory, px, py)

    terrain.generate()  # generate initial terrain

    while run:
        clock.tick(FPS)  # control the frame rate
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False  # exit loop on quit event
                break

            # handle keyboard events for terrain and player
            if event.type == pygame.KEYDOWN:
                terrain.on_event(event)
                player.on_event(event)

            if event.type == pygame.KEYUP:
                terrain.on_event(event)
                player.on_event(event)

            # handle mouse click events for terrain and inventory
            if event.type == pygame.MOUSEBUTTONDOWN:
                terrain.on_event(event)
                inventory.on_event(event)

        # update player and components each frame
        player.update(terrain)
        draw(terrain, inventory, player)
        terrain.update(player.vel)
        inventory.update()


# run the game if this file is executed directly
if __name__ == "__main__":
    main()
