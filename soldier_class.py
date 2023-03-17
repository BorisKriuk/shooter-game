import pygame
import os
import random
from bullet_class import Bullet
from utils import ANIMATION_COOLDOWN, GRAVITY, TILE_SIZE, SCREEN_WIDTH, SCROLL_THRESH, SCREEN_HEIGHT


class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        # create ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0

        # load all images for players
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in a folder
            num_of_frames = len(os.listdir(f'{self.char_type}/{animation}'))
            # print(num_of_frames)
            for i in range(num_of_frames):
                if animation == 'Run' and i == 6:
                    continue
                img = pygame.image.load(f'{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (img.get_width() * scale, img.get_height() * scale))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        # update shoot cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right, world, bg_scroll, water_group, exit_group):
        # reset movement variables
        screen_scroll = 0
        dx = 0
        dy = 0

        # assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1

        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # jump
        if self.jump and not self.in_air:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        # apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10

        dy += self.vel_y

        # check for collision
        for tile in world.obstacle_list:
            # check collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0

                # if the ai has hit the wall, make it turn around
                if self.char_type == 'Enemy':
                    self.direction *= (-1)
                    self.move_counter = 0

            # check for collision in y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                # check if below the ground
                if self.vel_y <= 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top

                # check if above the ground
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # check for collision with water
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        # check for collision with exit
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        # check if fallen from the map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        # check if going off the edges of the screen
        if self.char_type == 'Player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        # update scroll  based on player position
        if self.char_type == 'Player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH - 400)\
                    or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    def shoot(self, bullet_group, shot_fx):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + 0.75 * self.rect.size[0] * self.direction, self.rect.centery, self.direction)
            bullet_group.add(bullet)
            self.ammo -= 1
            shot_fx.play()

    def ai(self, player, bullet_group, world, screen_scroll, water_group, exit_group, shot_fx):
        if self.alive and player.alive:
            if not self.idling and random.randint(1, 200) == 1:
                self.update_action(0)  # 0: idle
                self.idling = True
                self.idling_counter = 50
            # check if ai is near the player
            if self.vision.colliderect(player.rect):
                # stop running and fac the player
                self.update_action(0)  # 0: idle

                # shoot the player
                self.shoot(bullet_group, shot_fx)
            else:
                if not self.idling:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right, world, screen_scroll, water_group, exit_group)
                    self.update_action(1)  # 1: run
                    self.move_counter += 1

                    # update ai vision as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

            # scroll
            self.rect.x += screen_scroll
        else:
            self.rect.x += screen_scroll
            self.idling_counter += 1
            if self.idling_counter >= 100:
                self.kill()

    def update_animation(self):
        # update animation

        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]

        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        # if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action])-1
            else:
                self.frame_index = 0

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def update_action(self, new_action):
        # check if the new action is different to  previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, screen):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)