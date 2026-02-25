
# main.py
import pygame
import time

import button

from settings import *
from assets_loader import load_assets
from simulation_stats import SimulationStats
from ui_sim import draw_text, draw_bg, draw_sim_hud, draw_sim_report
from world_map import World, inject_world_assets, load_level_csv, reset_level
import entities
from entities import Grenade



# ──────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Shooting Game")
    clock  = pygame.time.Clock()

    font = pygame.font.SysFont('Futura', 22)

    assets    = load_assets()
    tile_size = assets["TILE_SIZE"]

    front_back_img = pygame.image.load('assets/img/front_back.png').convert()
    front_back_img = pygame.transform.scale(front_back_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

    entities.inject_static_refs(
        screen=screen,
        tile_size=tile_size,
        item_boxes=assets["item_boxes"],
        bullet_img=assets["bullet_img"],
        grenade_img=assets["grenade_img"],
    )

    # SimulationStats() does NOT call reset() in __init__ anymore,
    # so run_id stays 0 until the player actually starts a game.
    sim = SimulationStats()

    groups = {
        "enemy_group":      pygame.sprite.Group(),
        "bullet_group":     pygame.sprite.Group(),
        "grenade_group":    pygame.sprite.Group(),
        "explosion_group":  pygame.sprite.Group(),
        "item_box_group":   pygame.sprite.Group(),
        "water_group":      pygame.sprite.Group(),
        "decoration_group": pygame.sprite.Group(),
        "exit_group":       pygame.sprite.Group(),
    }

    world = World()
    inject_world_assets(assets["img_list"], tile_size, groups)

    level          = 1
    game_state     = 'menu'   # 'menu' | 'config' | 'playing'
    game_completed = False

    world_data         = load_level_csv(f'assets/level{level}_data.csv', ROWS, COLS)
    player, health_bar = world.process_data(world_data)

    scroll_ref            = {"screen_scroll": 0, "bg_scroll": 0}
    enemy_vision_w_ref    = {"value": ENEMY_VISION_W}
    enemy_vision_h_ref    = {"value": ENEMY_VISION_H}
    enemy_idle_chance_ref = {"value": ENEMY_IDLE_CHANCE}

    def _inject():
        """Re-inject all refs into entities module after player/world changes."""
        entities.inject_game_refs(
            screen=screen,
            world=world,
            player=player,
            sim=sim,
            groups=groups,
            assets=assets,
            sim_tuning={
                "ENEMY_VISION_W_REF":    enemy_vision_w_ref,
                "ENEMY_VISION_H_REF":    enemy_vision_h_ref,
                "ENEMY_IDLE_CHANCE_REF": enemy_idle_chance_ref,
            },
            screen_scroll_ref=scroll_ref,
        )
        # Always keep sim aware of the current player object for path tracing
        sim.set_player_ref(player)

    _inject()

    start_button   = button.Button(SCREEN_WIDTH // 2 - 80,  SCREEN_HEIGHT // 2 - 110,
                                   assets["start_img"],   1)
    exit_button    = button.Button(SCREEN_WIDTH // 2 - 80,  SCREEN_HEIGHT // 2 + 50,
                                   assets["exit_img"],    1)
    restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50,
                                   assets["restart_img"], 1)
    quit_button    = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 140,
                                   assets["exit_img"],    1)

    moving_left    = False
    moving_right   = False
    shoot          = False
    grenade        = False
    grenade_thrown = False

    level_intro = LevelIntro()

    global SIM_SHOW_HUD
    run = True

    while run:
        clock.tick(FPS)

        # ── MENU ────────────────────────────────────────────────────────
        if game_state == 'menu':
            screen.blit(front_back_img, (0, 0))
            if start_button.draw(screen):
                game_state = 'config'
            if exit_button.draw(screen):
                run = False

        # ── CONFIG ──────────────────────────────────────────────────────
        elif game_state == 'config':
            result = draw_config_page(
                screen, clock, assets,
                init_vision_w    = enemy_vision_w_ref["value"],
                init_idle_chance = enemy_idle_chance_ref["value"],
            )
            if result is None:
                game_state = 'menu'
            else:
                enemy_vision_w_ref["value"], enemy_idle_chance_ref["value"] = result

                level          = 1
                game_completed = False
                scroll_ref["bg_scroll"] = 0

                # reset() increments run_id: 1st play → 1, 1st restart → 2, etc.
                sim.reset(level_started=level)

                world_data = reset_level(groups, ROWS, COLS)
                world_data = load_level_csv(f'assets/level{level}_data.csv', ROWS, COLS)
                world      = World()
                inject_world_assets(assets["img_list"], tile_size, groups)
                player, health_bar = world.process_data(world_data)
                _inject()   # also calls sim.set_player_ref(player)

                level_intro.trigger(level)
                game_state = 'playing'

        # ── PLAYING ─────────────────────────────────────────────────────
        elif game_state == 'playing':
            draw_bg(screen, scroll_ref["bg_scroll"], assets, SCREEN_WIDTH, SCREEN_HEIGHT)

            sim.tick_trace()   # ← records player x,y every frame

            world.draw(screen, scroll_ref["screen_scroll"])

            health_bar.draw(player.health)
            draw_text(screen, 'AMMO: ', font, WHITE, 10, 35)
            for x in range(player.ammo):
                screen.blit(assets["bullet_img"], (90 + (x * 10), 40))
            draw_text(screen, 'GRENADES: ', font, WHITE, 10, 60)
            for x in range(player.grenades):
                screen.blit(assets["grenade_img"], (135 + (x * 15), 62))

            if SIM_SHOW_HUD:
                draw_sim_hud(screen, font, sim,
                             enemy_vision_w_ref["value"],
                             enemy_idle_chance_ref["value"])

            player.update()
            player.draw()
            for enemy in groups["enemy_group"]:
                enemy.ai()
                enemy.update()
                enemy.draw()
            for g in groups.values():
                g.update()
            groups["bullet_group"].draw(screen)
            groups["grenade_group"].draw(screen)
            groups["explosion_group"].draw(screen)
            groups["item_box_group"].draw(screen)
            groups["water_group"].draw(screen)
            groups["decoration_group"].draw(screen)
            groups["exit_group"].draw(screen)

            level_intro.update_draw(screen)

            if player.alive and not game_completed:
                if shoot:
                    player.shoot()
                elif grenade and not grenade_thrown and player.grenades > 0:
                    g = Grenade(
                        player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),
                        player.rect.top, player.direction,
                    )
                    groups["grenade_group"].add(g)
                    player.grenades -= 1
                    grenade_thrown = True
                    sim.record_grenade_throw()

                if player.in_air:
                    player.update_action(2)
                elif moving_left or moving_right:
                    player.update_action(1)
                else:
                    player.update_action(0)

                scroll_ref["screen_scroll"], level_complete = player.move(moving_left, moving_right)
                scroll_ref["bg_scroll"] -= scroll_ref["screen_scroll"]

                if level_complete:
                    level += 1
                    scroll_ref["bg_scroll"] = 0
                    world_data = reset_level(groups, ROWS, COLS)
                    if level <= MAX_LEVELS:
                        world_data = load_level_csv(f'assets/level{level}_data.csv', ROWS, COLS)
                        world      = World()
                        inject_world_assets(assets["img_list"], tile_size, groups)
                        player, health_bar = world.process_data(world_data)
                        _inject()   # updates player ref in sim too
                        level_intro.trigger(level)
                    else:
                        game_completed = True
                        sim.ended_at   = time.time()
                        sim.save_outputs_once(final_level=MAX_LEVELS, completed=True)

            else:
                # ── game over / completed ──────────────────────────
                scroll_ref["screen_scroll"] = 0
                if sim.ended_at is None:
                    sim.ended_at = time.time()
                sim.save_outputs_once(final_level=min(level, MAX_LEVELS),
                                      completed=game_completed)

                report_bottom_y = draw_sim_report(
                    screen, font, sim,
                    completed        = game_completed,
                    final_level      = min(level, MAX_LEVELS),
                    enemy_vision_w   = enemy_vision_w_ref["value"],
                    enemy_idle_chance= enemy_idle_chance_ref["value"],
                    screen_w         = SCREEN_WIDTH,
                    screen_h         = SCREEN_HEIGHT,
                )

                btn_y = min(report_bottom_y + 25, SCREEN_HEIGHT - 80)
                restart_button.rect.topleft = (SCREEN_WIDTH // 2 - restart_button.rect.width - 15, btn_y)
                quit_button.rect.topleft    = (SCREEN_WIDTH // 2 + 15, btn_y)

                if restart_button.draw(screen):
                    # → config page; sim.reset() there will increment run_id
                    game_state = 'config'

                if quit_button.draw(screen):
                    run = False

        # ── EVENTS ──────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if game_state == 'playing':
                    if event.key == pygame.K_a:  moving_left  = True
                    if event.key == pygame.K_d:  moving_right = True
                    if event.key == pygame.K_q:  grenade      = True
                    if event.key == pygame.K_SPACE and player.alive:
                        shoot = True
                    if event.key == pygame.K_w and player.alive:
                        player.jump = True

                if event.key == pygame.K_ESCAPE:
                    run = False

                if event.key == pygame.K_F1:
                    SIM_SHOW_HUD = not SIM_SHOW_HUD
                if event.key == pygame.K_F2:
                    enemy_vision_w_ref["value"]    = max(60,  enemy_vision_w_ref["value"] - 20)
                if event.key == pygame.K_F3:
                    enemy_vision_w_ref["value"]    = min(400, enemy_vision_w_ref["value"] + 20)
                if event.key == pygame.K_F4:
                    enemy_idle_chance_ref["value"] = max(20,  enemy_idle_chance_ref["value"] - 20)
                if event.key == pygame.K_F5:
                    enemy_idle_chance_ref["value"] = min(600, enemy_idle_chance_ref["value"] + 20)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:     moving_left    = False
                if event.key == pygame.K_d:     moving_right   = False
                if event.key == pygame.K_SPACE: shoot          = False
                if event.key == pygame.K_q:
                    grenade        = False
                    grenade_thrown = False

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()