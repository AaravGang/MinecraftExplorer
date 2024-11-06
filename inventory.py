import pygame
from constants import *
pygame.font.init()  # initialize font module


class Inventory:
    def __init__(self, size, capcicty, x, y, tile_size):
        # initialize inventory properties
        self.size, self.capactiy = size, capcicty
        self.x, self.y, self.tile_size = x, y, tile_size * 2
        self.width, self.height = self.size * self.tile_size, self.tile_size

        # create the inventory rectangle and surface
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # set initial items and states
        self.storage = {"dirt": 5}
        self.types = ["dirt"]
        self.selected = "dirt"
        self.highlighted = None

    # add an item to inventory if there's space and capacity
    def add(self, item):
        if len(self.types) >= self.size:
            return False

        if item not in self.types:
            self.storage[item] = 1
            self.types.append(item)
            if len(self.types) == 1:
                self.selected = item
        elif self.storage[item] >= self.capactiy:
            return False
        else:
            self.storage[item] += 1

    # render inventory and items on screen
    def draw(self, surf):
        for i in range(self.size):
            pygame.draw.rect(self.surf, (255, 255, 255),
                             (i * self.tile_size, 0, self.tile_size, self.tile_size))

        for i, item in enumerate(self.storage):
            # draw item sprite in inventory slot
            self.surf.blit(pygame.transform.scale(TILE_LOOKUP[item]["sprites"][0],
                                                  (self.tile_size, self.tile_size)),
                           (i * self.tile_size, 0, self.tile_size, self.tile_size))

            # display item count in inventory
            myfont = pygame.font.SysFont(
                "arial", self.tile_size // 2, bold=True)
            label = myfont.render(
                str(self.storage[item]), True, (255, 20, 255))
            self.surf.blit(label, ((i) * self.tile_size, 0))

        # draw outlines around slots
        for i in range(self.size):
            pygame.draw.rect(self.surf, (0, 0, 0),
                             (i * self.tile_size, 0, self.tile_size, self.tile_size), 3)

        # highlight selected and hovered items
        if self.highlighted:
            i = self.types.index(self.highlighted)
            pygame.draw.rect(self.surf, (202, 97, 255),
                             (i * self.tile_size, 0, self.tile_size, self.tile_size), 3)

        if self.selected:
            i = self.types.index(self.selected)
            pygame.draw.rect(self.surf, (204, 231, 130),
                             (i * self.tile_size, 0, self.tile_size, self.tile_size), 3)

        surf.blit(self.surf, self.rect)

    # remove and return selected item if available
    def pop(self):
        type = None

        if not self.selected:
            if len(self.types) > 0:
                self.selected = self.types[0]
            else:
                return  # no items in inventory

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

    # handle mouse events to select inventory items
    def on_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.highlighted is not None:
                self.selected = self.highlighted

    # update highlighted item based on mouse position
    def update(self):
        x, y = pygame.mouse.get_pos()
        if self.y <= y <= self.y + self.height:
            col = (x - self.rect.left) // self.tile_size
            if len(self.types) > col:
                self.highlighted = self.types[col]
                return self.highlighted

        self.highlighted = None
