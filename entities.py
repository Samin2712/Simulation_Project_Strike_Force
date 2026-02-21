import os
import random
import pygame

from settings import GRAVITY, BLACK, RED, GREEN

# --- Module-level injected refs (set from main) ---
WORLD = None
PLAYER = None
SIM = None

ENEMY_VISION_W_REF = None
ENEMY_VISION_H_REF = None
ENEMY_IDLE_CHANCE_REF = None

SCREEN_SCROLL_REF = None

BULLET_GROUP = None
GRENADE_GROUP = None
EXPLOSION_GROUP = None
ENEMY_GROUP = None
WATER_GROUP = None
DECORATION_GROUP = None
EXIT_GROUP = None
ITEM_BOX_GROUP = None

BULLET_IMG = None
GRENADE_IMG = None
ITEM_BOXES = None
TILE_SIZE_REF = None

SCREEN = None

def inject_static_refs(screen, tile_size, item_boxes, bullet_img, grenade_img):
    global SCREEN, TILE_SIZE_REF, ITEM_BOXES, BULLET_IMG, GRENADE_IMG
    SCREEN = screen
    TILE_SIZE_REF = tile_size
    ITEM_BOXES = item_boxes
    BULLET_IMG = bullet_img
    GRENADE_IMG = grenade_img

def inject_game_refs(screen, world, player, sim, groups, assets, sim_tuning, screen_scroll_ref):
    global SCREEN, WORLD, PLAYER, SIM
    global BULLET_GROUP, GRENADE_GROUP, EXPLOSION_GROUP, ENEMY_GROUP, WATER_GROUP, DECORATION_GROUP, EXIT_GROUP, ITEM_BOX_GROUP
    global BULLET_IMG, GRENADE_IMG, ITEM_BOXES, TILE_SIZE_REF
    global ENEMY_VISION_W_REF, ENEMY_VISION_H_REF, ENEMY_IDLE_CHANCE_REF
    global SCREEN_SCROLL_REF


    SCREEN = screen
    WORLD = world
    PLAYER = player
    SIM = sim

    BULLET_GROUP = groups["bullet_group"]
    GRENADE_GROUP = groups["grenade_group"]
    EXPLOSION_GROUP = groups["explosion_group"]
    ENEMY_GROUP = groups["enemy_group"]
    WATER_GROUP = groups["water_group"]
    DECORATION_GROUP = groups["decoration_group"]
    EXIT_GROUP = groups["exit_group"]
    ITEM_BOX_GROUP = groups["item_box_group"]

    BULLET_IMG = assets["bullet_img"]
    GRENADE_IMG = assets["grenade_img"]
    ITEM_BOXES = assets["item_boxes"]
    TILE_SIZE_REF = assets["TILE_SIZE"]

    ENEMY_VISION_W_REF = sim_tuning["ENEMY_VISION_W_REF"]
    ENEMY_VISION_H_REF = sim_tuning["ENEMY_VISION_H_REF"]
    ENEMY_IDLE_CHANCE_REF = sim_tuning["ENEMY_IDLE_CHANCE_REF"]

    SCREEN_SCROLL_REF = screen_scroll_ref

class health_barr():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health
        ratio = self.health / self.max_health
        pygame.draw.rect(SCREEN, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(SCREEN, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(SCREEN, GREEN, (self.x, self.y, 150 * ratio, 20))

class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        super().__init__()
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.grenades = grenades
        self.start_ammo = ammo
        self.shoot_cooldown = 0
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
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 80)
        self.ideling = False
        self.ideling_counter = 0
        self.update_time = pygame.time.get_ticks()

        # --- Enemy AI state machine ---
        # States: 'patrol', 'alert', 'combat', 'search'
        self.ai_state = 'patrol'
        self.patrol_origin_x = x          # spawn X, used as patrol center
        self.patrol_half_range = 120       # tiles left/right of origin to patrol
        self.alert_timer = 0              # frames to stay alert after losing sight
        self.search_timer = 0             # frames to search after combat
        self.was_shot_at = False          # flagged when enemy takes a bullet hit
        self.react_turn_done = False      # has enemy turned to face attacker yet

        # analytics
        self.last_hit_by = None
        self.last_hit_method = 'bullet'

        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            temp_list = []
            num_of_frames = len(os.listdir(f'assets/img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'assets/img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
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
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        dx = 0
        dy = 0
        screen_scroll = 0

        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        if self.jump is True and self.in_air is False:
            self.vel_y = -13
            self.jump = False
            self.in_air = True

        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        for tile in WORLD.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                dx = 0
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                if self.vel_y < 0:
                    dy = tile[1].bottom - self.rect.top
                    self.vel_y = 0
                elif self.vel_y >= 0:
                    dy = tile[1].top - self.rect.bottom
                    self.vel_y = 0
                    self.in_air = False

        if pygame.sprite.spritecollide(self, WATER_GROUP, False):
            self.health = 0

        level_complete = False
        if pygame.sprite.spritecollide(self, EXIT_GROUP, False):
            level_complete = True

        # fall death
        from settings import SCREEN_HEIGHT, SCREEN_WIDTH, SCROLL_THRESH
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        self.rect.x += dx
        self.rect.y += dy

        if self.char_type == 'player':
            # scrolling
            from settings import SCREEN_WIDTH
            bg_scroll = SCREEN_SCROLL_REF["bg_scroll"]
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (WORLD.level_length * TILE_SIZE_REF) - SCREEN_WIDTH) or \
               (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete