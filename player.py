import pygame
from constants import *


class Player(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height):
        self.pos = pygame.Vector2(screen_width//2, screen_height//2)
        self.idle = []
        self.left_ = []
        self.right_ = []
        


    def load_sprites(self):
        pass