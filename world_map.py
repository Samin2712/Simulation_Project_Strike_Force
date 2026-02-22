# world_map.py
import csv
import pygame
from entities import Soldier, Water, Decoration, Exit, ItemBox, health_barr

# injected
IMG_LIST = None
TILE_SIZE = None

GROUPS = None

def inject_world_assets(img_list, tile_size, groups):
    global IMG_LIST, TILE_SIZE, GROUPS
    IMG_LIST = img_list
    TILE_SIZE = tile_size
    GROUPS = groups

class World:
    def __init__(self):
        self.obstacle_list = []
        self.level_length = 0

    def process_data(self, data):
        self.level_length = len(data[0])
        player = None
        hb = None

        for row_index, row in enumerate(data):
            for col_index, tile in enumerate(row):
                if tile >= 0:
                    img = IMG_LIST[tile]
                    img_rect = img.get_rect()
                    img_rect.x = col_index * TILE_SIZE
                    img_rect.y = row_index * TILE_SIZE
                    tile_data = (img, img_rect)

                    if 0 <= tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif 9 <= tile <= 10:
                        water = Water(img, col_index * TILE_SIZE, row_index * TILE_SIZE)
                        GROUPS["water_group"].add(water)
                    elif 11 <= tile <= 14:
                        decoration = Decoration(img, col_index * TILE_SIZE, row_index * TILE_SIZE)
                        GROUPS["decoration_group"].add(decoration)
                    elif tile == 15:
                        player = Soldier('player', col_index * TILE_SIZE, row_index * TILE_SIZE, 1.65, 5, 20, 5)
                        hb = health_barr(10, 10, player.health, player.max_health)
                    elif tile == 16:
                        enemy = Soldier('enemy', col_index * TILE_SIZE, row_index * TILE_SIZE, 1.65, 2, 20, 0)
                        GROUPS["enemy_group"].add(enemy)
                    elif tile == 17:
                        item_box = ItemBox('Ammo', col_index * TILE_SIZE, row_index * TILE_SIZE)
                        GROUPS["item_box_group"].add(item_box)
                    elif tile == 18:
                        item_box = ItemBox('Grenade', col_index * TILE_SIZE, row_index * TILE_SIZE)
                        GROUPS["item_box_group"].add(item_box)
                    elif tile == 19:
                        item_box = ItemBox('Health', col_index * TILE_SIZE, row_index * TILE_SIZE)
                        GROUPS["item_box_group"].add(item_box)
                    elif tile == 20:
                        exit_tile = Exit(img, col_index * TILE_SIZE, row_index * TILE_SIZE)
                        GROUPS["exit_group"].add(exit_tile)

        return player, hb

    def draw(self, screen, screen_scroll):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])

def load_level_csv(path, rows, cols):
    world_data = [[-1] * cols for _ in range(rows)]
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for x, row in enumerate(reader):
            for y, tile in enumerate(row):
                world_data[x][y] = int(tile)
    return world_data

def reset_level(groups, rows, cols):
    # clear groups (same behavior as typical reset)
    for g in groups.values():
        g.empty()
    return [[-1] * cols for _ in range(rows)]