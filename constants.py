# display constants
ROWS = 25
COLS = 50
TILE_SIZE = 32
WIDTH = COLS*TILE_SIZE
HEIGHT = ROWS*TILE_SIZE


# colors
SKY_COLOR = (164, 195, 234)


# tile info
TILE_LOOKUP = {"dirt": {"sprites": [], "bg_sprites": []},
               "gravel": {"sprites": [], "bg_sprites": []},
               "grass_dirt": {"sprites": [], "bg_sprites": []},
               "desert": {"sprites": [], "bg_sprites": []},
               "snow_dirt": {"sprites": [], "bg_sprites": []},
               "snow": {"sprites": [], "bg_sprites": []},
               "jungle": {"sprites": [], "bg_sprites": []},
               "stone": {"sprites": [], "bg_sprites": []},
               "water": {"sprites": [], "bg_sprites": []},
               "marsh": {"sprites": [], "bg_sprites": []},
               "netherite": {"sprites": [], "bg_sprites": [], "unbreakable": True},
               "portal": {"sprites": [], "bg_sprites": [], "unbreakable": True},
               "bg_dirt": {"sprites": [], "bg_sprites": []},
               "mountain": {"sprites": [], "bg_sprites": []},
               "ice": {"sprites": [], "bg_sprites": []},
               "bg_stone": {"sprites": [], "bg_sprites": []},
               "empty": {"sprites": [], "bg_sprites": []}}
