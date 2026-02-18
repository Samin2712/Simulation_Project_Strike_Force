# assets_loader.py
import pygame
from settings import SCREEN_HEIGHT, ROWS, TILE_TYPES,SCREEN_WIDTH

def load_assets():
    tile_size = SCREEN_HEIGHT // ROWS

    start_img = pygame.image.load('assets/img/start_btn.png')
    exit_img = pygame.image.load('assets/img/exit_btn.png')
    restart_img = pygame.image.load('assets/img/restart_btn.png')

    # Make RESTART same size as EXIT
    restart_img = pygame.transform.smoothscale(
        restart_img,
        exit_img.get_size()
    )

    pine1_img = pygame.image.load('assets/img/background/pine1.png').convert_alpha()
    pine2_img = pygame.image.load('assets/img/background/pine2.png').convert_alpha()
    mountain_img = pygame.image.load('assets/img/background/mountain1.png').convert_alpha()
    sky_img = pygame.image.load('assets/img/background/sky_cloud2.png').convert_alpha()
    #sky_img = pygame.transform.scale(sky_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

    img_list = []
    for x in range(TILE_TYPES):
        img = pygame.image.load(f'assets/img/tile/{x}.png').convert_alpha()
        img = pygame.transform.scale(img, (tile_size, tile_size))
        img_list.append(img)

    #bullet_img = pygame.image.load('assets/img/icons/bullet1.png').convert_alpha()
    bullet_img = pygame.image.load('assets/img/icons/bullet.png').convert_alpha()

    # 👇 ADD THIS LINE RIGHT HERE
    #bullet_img = pygame.transform.smoothscale(bullet_img, (12, 12))

    grenade_img = pygame.image.load('assets/img/icons/grenade.png').convert_alpha()

    item_boxes = {
        'Health': pygame.image.load('assets/img/icons/health_box.png').convert_alpha(),
        'Ammo': pygame.image.load('assets/img/icons/ammo_box.png').convert_alpha(),
        'Grenade': pygame.image.load('assets/img/icons/grenade_box.png').convert_alpha()
    }

    return {
        "TILE_SIZE": tile_size,
        "start_img": start_img,
        "exit_img": exit_img,
        "restart_img": restart_img,
        "pine1_img": pine1_img,
        "pine2_img": pine2_img,
        "mountain_img": mountain_img,
        "sky_img": sky_img,
        "img_list": img_list,
        "bullet_img": bullet_img,
        "grenade_img": grenade_img,
        "item_boxes": item_boxes,
    }