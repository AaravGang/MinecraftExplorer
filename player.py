import pygame
from constants import *


class Player:
    def __init__(self, screen_width, screen_height):
        self.pos = pygame.Vector2(screen_width//2, screen_height//2)


    def load_sprite(self):
        