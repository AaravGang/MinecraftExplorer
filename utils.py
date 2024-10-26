import pygame
import os


def create_sprites():
    tilemap = pygame.image.load(os.path.join(
        "assets", "sprites", "tilemap.png"))
    lookup = {"dirt": (0, 2), "snow_dirt": (4, 4), "grass_dirt": (0, 3), "jungle": (4, 6), "desert": (0, 4), "gravel": (1, 3), "stone": (1, 0), "water": (12, 15),
              "snow": (4, 2), "marsh": (3, 0), "netherite": (2, 5), "portal": (1, 7), "bg_dirt": (5, 6), "mountain": (2, 4), "ice": (4, 3), "bg_stone": (1, 1)}

    for type in lookup:
        pygame.image.save(pygame.transform.scale(tilemap.subsurface(
            (lookup[type][1]*16, lookup[type][0]*16, 16, 16)), (32, 32)), os.path.join("assets", "sprites", f"{type}.png"))
        print(f"loaded {type}")


create_sprites()
