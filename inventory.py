import pygame
from constants import *
pygame.font.init()


class Inventory:
    def __init__(self, size, capcicty, x, y, tile_size):
        self.size, self.capactiy = size, capcicty
        self.x, self.y, self.tile_size = x, y, tile_size*2
        self.width, self.height = self.size*self.tile_size, self.tile_size

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.surf = pygame.Surface(
            (self.width, self.height), pygame.SRCALPHA)

        self.storage = {"dirt": 5}
        self.types = ["dirt"]

        self.selected = "dirt"
        self.highlighted = None

    def add(self, item):
        if len(self.types) >= self.size:
            return False

        if not item in self.types:
            self.storage[item] = 1
            self.types.append(item)
            if len(self.types) == 1:
                self.selected = item

        elif self.storage[item] >= self.capactiy:
            return False
        else:
            self.storage[item] += 1

    def draw(self, surf):

        for i in range(self.size):
            pygame.draw.rect(self.surf, (255, 255, 255),
                             (i*self.tile_size, 0, self.tile_size, self.tile_size))

        for i, item in enumerate(self.storage):
            self.surf.blit(pygame.transform.scale(TILE_LOOKUP[item]["sprites"][0], (self.tile_size, self.tile_size)),
                           (i*self.tile_size, 0, self.tile_size, self.tile_size))

            myfont = pygame.font.SysFont("arial", self.tile_size//2, bold=True)
            label = myfont.render(
                str(self.storage[item]), True, (255, 20, 255))

            self.surf.blit(label, ((i)*self.tile_size, 0))

        for i in range(self.size):

            pygame.draw.rect(self.surf, (0, 0, 0),
                             (i*self.tile_size, 0, self.tile_size, self.tile_size), 3)

        if self.highlighted:
            i = self.types.index(self.highlighted)
            pygame.draw.rect(self.surf, (202, 97, 255),
                             (i*self.tile_size, 0, self.tile_size, self.tile_size), 3),

        if self.selected:
            i = self.types.index(self.selected)
            pygame.draw.rect(self.surf, (204, 231, 130),
                             (i*self.tile_size, 0, self.tile_size, self.tile_size), 3)

        surf.blit(self.surf, self.rect)

    def pop(self):
        type = None

        if not self.selected:
            if len(self.types) > 0:
                self.selected = self.types[0]

            # no items in inventory
            else:
                return

        if self.storage[self.selected] > 0:
            self.storage[self.selected] -= 1
            type = self.selected
            if self.storage[self.selected] == 0:
                self.storage.pop(self.selected)
                self.types.remove(self.selected)
                self.selected = None

                if len(self.types) > 0:
                    self.selected = self.types[0]

        return type

    def on_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.highlighted is not None:
                self.selected = self.highlighted

    def update(self):
        x, y = pygame.mouse.get_pos()

        if self.y <= y <= self.y+self.height:
            col = (x-self.rect.left)//self.tile_size
            if len(self.types) > col:
                self.highlighted = self.types[col]
                return self.highlighted

        self.highlighted = None
