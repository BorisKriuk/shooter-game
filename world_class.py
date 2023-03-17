from soldier_class import Soldier
from health_bar_class import HealthBar
from item_box_class import ItemBox
from decoration_class import Decoration
from water_class import Water
from exit_class import Exit
from utils import IMG_LIST, TILE_SIZE


class World:
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data, enemy_group, item_box_group, item_boxes, decoration_group, water_group, exit_group):
        self.level_length = len(data[0])

        # iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = IMG_LIST[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if 0 <= tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif 9 <= tile <= 10:
                        # water
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)

                    elif 11 <= tile <= 14:
                        # decoration
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)

                    elif tile == 15:
                        # create a player
                        player = Soldier('Player', x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 4)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16:
                        # create enemies
                        enemy = Soldier('Enemy', x * TILE_SIZE, y * TILE_SIZE, 1.65, 3, 20, 0)
                        enemy_group.add(enemy)
                    elif tile == 17:
                        # create ammo box
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE, item_boxes)
                        item_box_group.add(item_box)
                    elif tile == 18:
                        # create grenade box
                        item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE, item_boxes)
                        item_box_group.add(item_box)
                    elif tile == 19:
                        # create health box
                        item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE, item_boxes)
                        item_box_group.add(item_box)
                    elif tile == 20:
                        # create exit
                        game_exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(game_exit)

        return player, health_bar

    def draw(self, screen, screen_scroll):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])