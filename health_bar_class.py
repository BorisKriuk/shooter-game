import pygame
from utils import RED, GREEN, BLACK


class HealthBar:
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health, screen):
        # update with new health
        self.health = health

        # calculate health ratio
        ratio = self.health / self.max_health
        if ratio > 1:
            ratio = 1
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150*ratio, 20))