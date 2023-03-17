import pygame
from pygame import mixer
from grenade_class import Grenade
from world_class import World
from button_class import Button
from screen_fade_class import ScreenFade
from utils import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BG, HEALTH_BOX_IMG, GRENADE_BOX_IMG, AMMO_BOX_IMG, WHITE,\
    BULLET_IMG, GRENADE_IMG, ROWS, COLS, LEVEL1, MOUNTAIN_IMG, PINE1_IMG, PINE2_IMG, SKY_IMG, START_IMG, EXIT_IMG,\
    RESTART_IMG, MAX_LEVELS, PINK, BLACK


def draw_text(text, current_font, text_col, x, y):
    img = current_font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    screen.fill(BG)
    width = SKY_IMG.get_width()
    for x in range(5):
        screen.blit(SKY_IMG, (x * width - bg_scroll * 0.5, 0))
        screen.blit(MOUNTAIN_IMG, (x * width - bg_scroll * 0.6, SCREEN_HEIGHT - MOUNTAIN_IMG.get_height() - 300))
        screen.blit(PINE1_IMG, (x * width - bg_scroll * 0.7, SCREEN_HEIGHT - PINE1_IMG.get_height() - 150))
        screen.blit(PINE2_IMG, (x * width - bg_scroll * 0.8, SCREEN_HEIGHT - PINE2_IMG.get_height()))


# function to reset level
def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    # create empty tile list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data


pygame.init()
mixer.init()

# load music and sounds
pygame.mixer.music.load('Audio/audio_music2.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)

jump_fx = pygame.mixer.Sound('Audio/audio_jump.wav')
jump_fx.set_volume(0.5)

shot_fx = pygame.mixer.Sound('Audio/audio_shot.wav')
shot_fx.set_volume(0.5)

grenade_fx = pygame.mixer.Sound('Audio/audio_grenade.wav')
grenade_fx.set_volume(0.5)

# create screen fades
death_fade = ScreenFade(2, PINK, 4)
intro_fade = ScreenFade(1, BLACK, 4)

# define game variables
level = 1
screen_scroll = 0
bg_scroll = 0
start_game = False
start_intro = False

# define font
font = pygame.font.SysFont('Futura', 20)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Platformer 2.0")

clock = pygame.time.Clock()

# define player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

item_boxes = {
    'Health': HEALTH_BOX_IMG,
    'Ammo': AMMO_BOX_IMG,
    'Grenade': GRENADE_BOX_IMG
}

x = 200
y = 200
# scale = 3

# create buttons
start_button = Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, START_IMG, screen)
exit_button = Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, EXIT_IMG, screen)
restart_button = Button(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 - 50, RESTART_IMG, screen)

# create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

# load in world data and create world
for x, row in enumerate(LEVEL1):
    for y, tile in enumerate(row):
        world_data[x][y] = int(tile)

world = World()
player, health_bar = world.process_data(world_data, enemy_group, item_box_group, item_boxes, decoration_group,
                                        water_group, exit_group)


running = True
while running:

    clock.tick(FPS)

    if not start_game:
        # draw menu
        screen.fill(BG)

        # add buttons
        if start_button.draw():
            start_game = True
            start_intro = True
        if exit_button.draw():
            running = False

    else:

        # draw background
        draw_bg()

        # draw world map
        world.draw(screen, screen_scroll)

        # show player health
        health_bar.draw(player.health, screen)

        # show ammo
        draw_text(f'AMMO: ', font, WHITE, 10, 35)
        for x in range(player.ammo):
            screen.blit(BULLET_IMG, (90+(x*10), 45))
        # show grenades
        draw_text(f'GRENADES: ', font, WHITE, 10, 60)
        for x in range(player.grenades):
            screen.blit(GRENADE_IMG, (130+(x*14), 68))

        player.update()
        player.draw(screen)

        for enemy in enemy_group:
            enemy.ai(player, bullet_group, world, screen_scroll, water_group, exit_group, shot_fx)
            enemy.update()
            enemy.draw(screen)

        # update and draw groups
        bullet_group.update(player, enemy, bullet_group, enemy_group, world, screen_scroll)
        bullet_group.draw(screen)

        grenade_group.update(explosion_group, player, enemy_group, world, screen_scroll, grenade_fx)
        grenade_group.draw(screen)

        explosion_group.update(screen_scroll)
        explosion_group.draw(screen)

        item_box_group.update(player, screen_scroll)
        item_box_group.draw(screen)

        decoration_group.update(screen_scroll)
        decoration_group.draw(screen)

        water_group.update(screen_scroll)
        water_group.draw(screen)

        exit_group.update(screen_scroll)
        exit_group.draw(screen)

        # show intro
        if start_intro:
            if intro_fade.fade(screen):
                start_intro = False
                intro_fade.fade_counter = 0

        # update player actions
        if player.alive:
            # shoot bullets
            if shoot:
                player.shoot(bullet_group, shot_fx)

            # throw grenades
            elif grenade and not grenade_thrown and player.grenades > 0:
                grenade = Grenade(player.rect.centerx+int(player.rect.size[0]*0.5*player.direction),
                                  player.rect.top, player.direction)
                grenade_group.add(grenade)

                # reduce grenades
                grenade_thrown = True
                player.grenades -= 1

            if player.in_air:
                player.update_action(2)  # means jump mode
            elif moving_left or moving_right:
                player.update_action(1)  # 1 means run mode
            else:
                player.update_action(0)  # means idle mode
            screen_scroll, level_complete = player.move(moving_left, moving_right, world, bg_scroll, water_group, exit_group)
            bg_scroll -= screen_scroll

            # check if player has completed the level
            if level_complete:
                start_intro = True
                try:
                    level += 1
                    bg_scroll = 0
                    world_data = reset_level()
                    if level <= MAX_LEVELS:
                        for x, row in enumerate(LEVEL1):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                        world = World()
                        player, health_bar = world.process_data(world_data, enemy_group, item_box_group, item_boxes,
                                                                decoration_group,
                                                                water_group, exit_group)
                except Exception:
                    bg_scroll = 0
                    world_data = reset_level()
                    for x, row in enumerate(LEVEL1):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data, enemy_group, item_box_group, item_boxes,
                                                            decoration_group,
                                                            water_group, exit_group)
        else:
            for enemy in enemy_group:
                enemy.update_action(0)
            screen_scroll = 0
            if death_fade.fade(screen):
                if restart_button.draw():
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = reset_level()
                    for x, row in enumerate(LEVEL1):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data, enemy_group, item_box_group, item_boxes,
                                                            decoration_group,
                                                            water_group, exit_group)

    for event in pygame.event.get():
        # quit the game
        if event.type == pygame.QUIT:
            running = False

        # keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                grenade = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                running = False

        # keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False

    pygame.display.update()

pygame.quit()
