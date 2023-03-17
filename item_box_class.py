import pygame
from utils import TILE_SIZE


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y, item_boxes):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x+TILE_SIZE//2, y+TILE_SIZE-self.image.get_height())

    def update(self, player, screen_scroll):
        # scroll
        self.rect.x += screen_scroll

        # check if the player has picked up the box
        if pygame.sprite.collide_rect(self, player):
            # check what kind of box that was
            if self.item_type == 'Health':
                if player.health <= player.max_health:
                    player.health += 50
            elif self.item_type == 'Ammo':
                player.ammo += 10
            elif self.item_type == 'Grenade':
                player.grenades += 2
            # delete the item box
            self.kill()

