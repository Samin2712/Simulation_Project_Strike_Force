# import pygame
# import time

# import button

# from settings import *
# from assets_loader import load_assets
# from simulation_stats import SimulationStats
# from ui_sim import draw_text, draw_bg, draw_sim_hud, draw_sim_report
# from world_map import World, inject_world_assets, load_level_csv, reset_level
# import entities
# from entities import Grenade


# # ──────────────────────────────────────────────
# #  SLIDER WIDGET
# # ──────────────────────────────────────────────

# class Slider:
#     def __init__(self, x, y, w, min_val, max_val, init_val, step=10, label=""):
#         self.x = x
#         self.y = y
#         self.w = w
#         self.h = 8
#         self.min_val  = min_val
#         self.max_val  = max_val
#         self.value    = init_val
#         self.step     = step
#         self.label    = label
#         self.dragging = False
#         self.knob_r   = 12

#     def _knob_x(self):
#         t = (self.value - self.min_val) / (self.max_val - self.min_val)
#         return int(self.x + t * self.w)

#     def draw(self, screen, font):
#         cy = self.y + self.knob_r
#         pygame.draw.rect(screen, (55, 55, 65),
#                          (self.x, cy - self.h // 2, self.w, self.h), border_radius=4)
#         kx = self._knob_x()
#         if kx > self.x:
#             pygame.draw.rect(screen, (220, 45, 55),
#                              (self.x, cy - self.h // 2, kx - self.x, self.h), border_radius=4)
#         pygame.draw.circle(screen, (220, 45, 55), (kx, cy), self.knob_r)
#         pygame.draw.circle(screen, (235, 235, 245), (kx, cy), self.knob_r - 4)
#         lbl = font.render(f"{self.label}:  {self.value}", True, (240, 240, 250))
#         screen.blit(lbl, (self.x, self.y - 30))

#     def handle_event(self, event):
#         if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
#             kx = self._knob_x()
#             cy = self.y + self.knob_r
#             if abs(event.pos[0] - kx) <= self.knob_r + 6 and abs(event.pos[1] - cy) <= self.knob_r + 6:
#                 self.dragging = True
#         if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
#             self.dragging = False
#         if event.type == pygame.MOUSEMOTION and self.dragging:
#             rel_x = max(0, min(self.w, event.pos[0] - self.x))
#             raw   = self.min_val + (rel_x / self.w) * (self.max_val - self.min_val)
#             self.value = int(round(raw / self.step) * self.step)
#             self.value = max(self.min_val, min(self.max_val, self.value))


# # ──────────────────────────────────────────────
# #  CONFIG PAGE
# # ──────────────────────────────────────────────

# def draw_config_page(screen, clock, assets, init_vision_w, init_idle_chance):
#     """
#     Settings page between menu and game.
#     Background = game parallax bg.
#     PLAY button = the same start_img used on the main menu.
#     Returns (vision_w, idle_chance) or None (ESC → back to menu).
#     """
#     W, H = screen.get_size()
#     font_title = pygame.font.SysFont('Futura', 28, bold=True)
#     font_med   = pygame.font.SysFont('Futura', 20)
#     font_small = pygame.font.SysFont('Futura', 15)

#     slider_w = int(W * 0.55)
#     cx = W // 2

#     slider_vision = Slider(cx - slider_w // 2, int(H * 0.40),
#                            slider_w, 60, 400, init_vision_w, step=10,
#                            label="Enemy Vision Width")
#     slider_idle   = Slider(cx - slider_w // 2, int(H * 0.57),
#                            slider_w, 20, 600, init_idle_chance, step=20,
#                            label="Enemy Idle Chance  (1 / N)")

#     # Use the real start_img button
#     start_img = assets["start_img"]
#     play_btn  = button.Button(cx - start_img.get_width() // 2,
#                               int(H * 0.73), start_img, 1)

#     fade = 255

#     while True:
#         clock.tick(60)

#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 return None
#             if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
#                 return None
#             slider_vision.handle_event(event)
#             slider_idle.handle_event(event)

#         draw_bg(screen, 0, assets, W, H)

#         panel_w = int(W * 0.70)
#         panel_h = int(H * 0.68)
#         panel   = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
#         panel.fill((8, 8, 12, 205))
#         px = (W - panel_w) // 2
#         py = int(H * 0.13)
#         screen.blit(panel, (px, py))
#         pygame.draw.rect(screen, (220, 45, 55), (px, py, panel_w, panel_h), 2, border_radius=3)

#         t_surf = font_title.render("MISSION  SETTINGS", True, (255, 255, 255))
#         screen.blit(t_surf, t_surf.get_rect(centerx=cx, y=py + 18))
#         pygame.draw.line(screen, (220, 45, 55),
#                          (px + 28, py + 58), (px + panel_w - 28, py + 58), 1)

#         slider_vision.draw(screen, font_med)
#         slider_idle.draw(screen, font_med)

#         h1 = font_small.render(
#             "Smaller vision = enemies harder to spot you      |      Higher N = enemies idle less often",
#             True, (155, 165, 175))
#         h2 = font_small.render(
#             "Live tuning during gameplay:   F2 / F3  Vision      F4 / F5  Idle      F1  Toggle HUD",
#             True, (110, 120, 130))
#         screen.blit(h1, h1.get_rect(centerx=cx, y=int(H * 0.68)))
#         screen.blit(h2, h2.get_rect(centerx=cx, y=int(H * 0.71)))

#         if play_btn.draw(screen):
#             return slider_vision.value, slider_idle.value

#         if fade > 0:
#             fo = pygame.Surface((W, H))
#             fo.fill((0, 0, 0))
#             fo.set_alpha(fade)
#             screen.blit(fo, (0, 0))
#             fade = max(0, fade - 12)

#         pygame.display.flip()


# # ──────────────────────────────────────────────
# #  LEVEL INTRO FLOATING TEXT
# # ──────────────────────────────────────────────

# class LevelIntro:
#     FADE_IN  = 45
#     HOLD     = 90
#     FADE_OUT = 55

#     def __init__(self):
#         self.active = False
#         self.timer  = 0
#         self.level  = 1
#         self._font  = None

#     def _get_font(self):
#         if self._font is None:
#             for name in ['Arial Black', 'Impact', 'Arial', 'Verdana']:
#                 try:
#                     f = pygame.font.SysFont(name, 80, bold=True)
#                     f.render("TEST", True, (255, 255, 255))
#                     self._font = f
#                     break
#                 except Exception:
#                     pass
#             if self._font is None:
#                 self._font = pygame.font.Font(None, 80)
#         return self._font

#     def trigger(self, level: int):
#         self.level  = level
#         self.timer  = self.FADE_IN + self.HOLD + self.FADE_OUT
#         self.active = True

#     def update_draw(self, screen: pygame.Surface):
#         if not self.active:
#             return
#         self.timer -= 1
#         if self.timer <= 0:
#             self.active = False
#             return

#         total   = self.FADE_IN + self.HOLD + self.FADE_OUT
#         elapsed = total - self.timer
#         if elapsed < self.FADE_IN:
#             alpha = int(255 * elapsed / self.FADE_IN)
#         elif elapsed < self.FADE_IN + self.HOLD:
#             alpha = 255
#         else:
#             p     = elapsed - self.FADE_IN - self.HOLD
#             alpha = int(255 * (1.0 - p / self.FADE_OUT))
#         alpha = max(0, min(255, alpha))

#         W, H   = screen.get_size()
#         font   = self._get_font()
#         text   = f"LEVEL  {self.level}"
#         main_s = font.render(text, True, (255, 255, 255))
#         tw, th = main_s.get_size()
#         pad    = 30
#         bar_h  = 5
#         cw     = tw + pad * 2
#         ch     = th + bar_h + 16

#         comp   = pygame.Surface((cw, ch), pygame.SRCALPHA)
#         shadow = font.render(text, True, (10, 10, 10))
#         comp.blit(shadow, (pad + 4, 4))
#         comp.blit(main_s, (pad, 0))
#         pygame.draw.rect(comp, (220, 45, 55), (pad, th + 8, tw, bar_h))
#         comp.set_alpha(alpha)
#         screen.blit(comp, (W // 2 - cw // 2, H // 2 - ch // 2))


# # ──────────────────────────────────────────────
# #  MAIN
# # ──────────────────────────────────────────────

# def main():
#     pygame.init()
#     screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
#     pygame.display.set_caption("Shooting Game")
#     clock  = pygame.time.Clock()

#     font = pygame.font.SysFont('Futura', 22)

#     assets    = load_assets()
#     tile_size = assets["TILE_SIZE"]

#     front_back_img = pygame.image.load('assets/img/front_back.png').convert()
#     front_back_img = pygame.transform.scale(front_back_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

#     entities.inject_static_refs(
#         screen=screen,
#         tile_size=tile_size,
#         item_boxes=assets["item_boxes"],
#         bullet_img=assets["bullet_img"],
#         grenade_img=assets["grenade_img"],
#     )

#     # SimulationStats() does NOT call reset() in __init__ anymore,
#     # so run_id stays 0 until the player actually starts a game.
#     sim = SimulationStats()

#     groups = {
#         "enemy_group":      pygame.sprite.Group(),
#         "bullet_group":     pygame.sprite.Group(),
#         "grenade_group":    pygame.sprite.Group(),
#         "explosion_group":  pygame.sprite.Group(),
#         "item_box_group":   pygame.sprite.Group(),
#         "water_group":      pygame.sprite.Group(),
#         "decoration_group": pygame.sprite.Group(),
#         "exit_group":       pygame.sprite.Group(),
#     }

#     world = World()
#     inject_world_assets(assets["img_list"], tile_size, groups)

#     level          = 1
#     game_state     = 'menu'   # 'menu' | 'config' | 'playing'
#     game_completed = False

#     world_data         = load_level_csv(f'assets/level{level}_data.csv', ROWS, COLS)
#     player, health_bar = world.process_data(world_data)

#     scroll_ref            = {"screen_scroll": 0, "bg_scroll": 0}
#     enemy_vision_w_ref    = {"value": ENEMY_VISION_W}
#     enemy_vision_h_ref    = {"value": ENEMY_VISION_H}
#     enemy_idle_chance_ref = {"value": ENEMY_IDLE_CHANCE}

#     def _inject():
#         """Re-inject all refs into entities module after player/world changes."""
#         entities.inject_game_refs(
#             screen=screen,
#             world=world,
#             player=player,
#             sim=sim,
#             groups=groups,
#             assets=assets,
#             sim_tuning={
#                 "ENEMY_VISION_W_REF":    enemy_vision_w_ref,
#                 "ENEMY_VISION_H_REF":    enemy_vision_h_ref,
#                 "ENEMY_IDLE_CHANCE_REF": enemy_idle_chance_ref,
#             },
#             screen_scroll_ref=scroll_ref,
#         )
#         # Always keep sim aware of the current player object for path tracing
#         sim.set_player_ref(player)

#     _inject()

#     start_button   = button.Button(SCREEN_WIDTH // 2 - 80,  SCREEN_HEIGHT // 2 - 110,
#                                    assets["start_img"],   1)
#     exit_button    = button.Button(SCREEN_WIDTH // 2 - 80,  SCREEN_HEIGHT // 2 + 50,
#                                    assets["exit_img"],    1)
#     restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50,
#                                    assets["restart_img"], 1)
#     quit_button    = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 140,
#                                    assets["exit_img"],    1)

#     moving_left    = False
#     moving_right   = False
#     shoot          = False
#     grenade        = False
#     grenade_thrown = False

#     level_intro = LevelIntro()

#     global SIM_SHOW_HUD
#     run = True

#     while run:
#         clock.tick(FPS)

#         # ── MENU ────────────────────────────────────────────────────────
#         if game_state == 'menu':
#             screen.blit(front_back_img, (0, 0))
#             if start_button.draw(screen):
#                 game_state = 'config'
#             if exit_button.draw(screen):
#                 run = False

#         # ── CONFIG ──────────────────────────────────────────────────────
#         elif game_state == 'config':
#             result = draw_config_page(
#                 screen, clock, assets,
#                 init_vision_w    = enemy_vision_w_ref["value"],
#                 init_idle_chance = enemy_idle_chance_ref["value"],
#             )
#             if result is None:
#                 game_state = 'menu'
#             else:
#                 enemy_vision_w_ref["value"], enemy_idle_chance_ref["value"] = result

#                 level          = 1
#                 game_completed = False
#                 scroll_ref["bg_scroll"] = 0

#                 # reset() increments run_id: 1st play → 1, 1st restart → 2, etc.
#                 sim.reset(level_started=level)

#                 world_data = reset_level(groups, ROWS, COLS)
#                 world_data = load_level_csv(f'assets/level{level}_data.csv', ROWS, COLS)
#                 world      = World()
#                 inject_world_assets(assets["img_list"], tile_size, groups)
#                 player, health_bar = world.process_data(world_data)
#                 _inject()   # also calls sim.set_player_ref(player)

#                 level_intro.trigger(level)
#                 game_state = 'playing'

#         # ── PLAYING ─────────────────────────────────────────────────────
#         elif game_state == 'playing':
#             draw_bg(screen, scroll_ref["bg_scroll"], assets, SCREEN_WIDTH, SCREEN_HEIGHT)

#             sim.tick_trace()   # ← records player x,y every frame

#             world.draw(screen, scroll_ref["screen_scroll"])

#             health_bar.draw(player.health)
#             draw_text(screen, 'AMMO: ', font, WHITE, 10, 35)
#             for x in range(player.ammo):
#                 screen.blit(assets["bullet_img"], (90 + (x * 10), 40))
#             draw_text(screen, 'GRENADES: ', font, WHITE, 10, 60)
#             for x in range(player.grenades):
#                 screen.blit(assets["grenade_img"], (135 + (x * 15), 62))

#             if SIM_SHOW_HUD:
#                 draw_sim_hud(screen, font, sim,
#                              enemy_vision_w_ref["value"],
#                              enemy_idle_chance_ref["value"])

#             player.update()
#             player.draw()
#             for enemy in groups["enemy_group"]:
#                 enemy.ai()
#                 enemy.update()
#                 enemy.draw()
#             for g in groups.values():
#                 g.update()
#             groups["bullet_group"].draw(screen)
#             groups["grenade_group"].draw(screen)
#             groups["explosion_group"].draw(screen)
#             groups["item_box_group"].draw(screen)
#             groups["water_group"].draw(screen)
#             groups["decoration_group"].draw(screen)
#             groups["exit_group"].draw(screen)

#             level_intro.update_draw(screen)

#             if player.alive and not game_completed:
#                 if shoot:
#                     player.shoot()
#                 elif grenade and not grenade_thrown and player.grenades > 0:
#                     g = Grenade(
#                         player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),
#                         player.rect.top, player.direction,
#                     )
#                     groups["grenade_group"].add(g)
#                     player.grenades -= 1
#                     grenade_thrown = True
#                     sim.record_grenade_throw()

#                 if player.in_air:
#                     player.update_action(2)
#                 elif moving_left or moving_right:
#                     player.update_action(1)
#                 else:
#                     player.update_action(0)

#                 scroll_ref["screen_scroll"], level_complete = player.move(moving_left, moving_right)
#                 scroll_ref["bg_scroll"] -= scroll_ref["screen_scroll"]

#                 if level_complete:
#                     level += 1
#                     scroll_ref["bg_scroll"] = 0
#                     world_data = reset_level(groups, ROWS, COLS)
#                     if level <= MAX_LEVELS:
#                         world_data = load_level_csv(f'assets/level{level}_data.csv', ROWS, COLS)
#                         world      = World()
#                         inject_world_assets(assets["img_list"], tile_size, groups)
#                         player, health_bar = world.process_data(world_data)
#                         _inject()   # updates player ref in sim too
#                         level_intro.trigger(level)
#                     else:
#                         game_completed = True
#                         sim.ended_at   = time.time()
#                         sim.save_outputs_once(final_level=MAX_LEVELS, completed=True)

#             else:
#                 # ── game over / completed ──────────────────────────
#                 scroll_ref["screen_scroll"] = 0
#                 if sim.ended_at is None:
#                     sim.ended_at = time.time()
#                 sim.save_outputs_once(final_level=min(level, MAX_LEVELS),
#                                       completed=game_completed)

#                 report_bottom_y = draw_sim_report(
#                     screen, font, sim,
#                     completed        = game_completed,
#                     final_level      = min(level, MAX_LEVELS),
#                     enemy_vision_w   = enemy_vision_w_ref["value"],
#                     enemy_idle_chance= enemy_idle_chance_ref["value"],
#                     screen_w         = SCREEN_WIDTH,
#                     screen_h         = SCREEN_HEIGHT,
#                 )

#                 btn_y = min(report_bottom_y + 25, SCREEN_HEIGHT - 80)
#                 restart_button.rect.topleft = (SCREEN_WIDTH // 2 - restart_button.rect.width - 15, btn_y)
#                 quit_button.rect.topleft    = (SCREEN_WIDTH // 2 + 15, btn_y)

#                 if restart_button.draw(screen):
#                     # → config page; sim.reset() there will increment run_id
#                     game_state = 'config'

#                 if quit_button.draw(screen):
#                     run = False

#         # ── EVENTS ──────────────────────────────────────────────────────
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 run = False

#             if event.type == pygame.KEYDOWN:
#                 if game_state == 'playing':
#                     if event.key == pygame.K_a:  moving_left  = True
#                     if event.key == pygame.K_d:  moving_right = True
#                     if event.key == pygame.K_q:  grenade      = True
#                     if event.key == pygame.K_SPACE and player.alive:
#                         shoot = True
#                     if event.key == pygame.K_w and player.alive:
#                         player.jump = True

#                 if event.key == pygame.K_ESCAPE:
#                     run = False

#                 if event.key == pygame.K_F1:
#                     SIM_SHOW_HUD = not SIM_SHOW_HUD
#                 if event.key == pygame.K_F2:
#                     enemy_vision_w_ref["value"]    = max(60,  enemy_vision_w_ref["value"] - 20)
#                 if event.key == pygame.K_F3:
#                     enemy_vision_w_ref["value"]    = min(400, enemy_vision_w_ref["value"] + 20)
#                 if event.key == pygame.K_F4:
#                     enemy_idle_chance_ref["value"] = max(20,  enemy_idle_chance_ref["value"] - 20)
#                 if event.key == pygame.K_F5:
#                     enemy_idle_chance_ref["value"] = min(600, enemy_idle_chance_ref["value"] + 20)

#             if event.type == pygame.KEYUP:
#                 if event.key == pygame.K_a:     moving_left    = False
#                 if event.key == pygame.K_d:     moving_right   = False
#                 if event.key == pygame.K_SPACE: shoot          = False
#                 if event.key == pygame.K_q:
#                     grenade        = False
#                     grenade_thrown = False

#         pygame.display.update()

#     pygame.quit()


# if __name__ == "__main__":
#     main()



import pygame
import time

import button

from settings import *
from assets_loader import load_assets
from simulation_stats import SimulationStats
from ui_sim import draw_text, draw_bg, draw_sim_hud, draw_sim_report, draw_dynamic_hud
from world_map import World, inject_world_assets, load_level_csv, reset_level
import entities
from entities import Grenade
from dynamic_ai import DynamicAI
from experiment_mode import ExperimentManager


# ──────────────────────────────────────────────
#  SLIDER WIDGET
# ──────────────────────────────────────────────

class Slider:
    def __init__(self, x, y, w, min_val, max_val, init_val, step=10, label=""):
        self.x = x
        self.y = y
        self.w = w
        self.h = 8
        self.min_val  = min_val
        self.max_val  = max_val
        self.value    = init_val
        self.step     = step
        self.label    = label
        self.dragging = False
        self.knob_r   = 12

    def _knob_x(self):
        t = (self.value - self.min_val) / (self.max_val - self.min_val)
        return int(self.x + t * self.w)

    def draw(self, screen, font):
        cy = self.y + self.knob_r
        pygame.draw.rect(screen, (55, 55, 65),
                         (self.x, cy - self.h // 2, self.w, self.h), border_radius=4)
        kx = self._knob_x()
        if kx > self.x:
            pygame.draw.rect(screen, (220, 45, 55),
                             (self.x, cy - self.h // 2, kx - self.x, self.h), border_radius=4)
        pygame.draw.circle(screen, (220, 45, 55), (kx, cy), self.knob_r)
        pygame.draw.circle(screen, (235, 235, 245), (kx, cy), self.knob_r - 4)
        lbl = font.render(f"{self.label}:  {self.value}", True, (240, 240, 250))
        screen.blit(lbl, (self.x, self.y - 30))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            kx = self._knob_x()
            cy = self.y + self.knob_r
            if abs(event.pos[0] - kx) <= self.knob_r + 6 and abs(event.pos[1] - cy) <= self.knob_r + 6:
                self.dragging = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        if event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = max(0, min(self.w, event.pos[0] - self.x))
            raw   = self.min_val + (rel_x / self.w) * (self.max_val - self.min_val)
            self.value = int(round(raw / self.step) * self.step)
            self.value = max(self.min_val, min(self.max_val, self.value))


# ──────────────────────────────────────────────
#  MODE SELECTION SCREEN
# ──────────────────────────────────────────────

def draw_mode_select(screen, clock, assets):
    W, H = screen.get_size()
    font_title = pygame.font.SysFont('Futura', 32, bold=True)
    font_sub   = pygame.font.SysFont('Futura', 14)

    def make_mode_btn(label, subtitle, accent):
        bw, bh = 230, 122
        surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        surf.fill((20, 20, 28, 220))
        pygame.draw.rect(surf, accent, (0, 0, bw, bh), 3, border_radius=6)
        txt = font_sub.render(label, True, (240, 240, 250))
        surf.blit(txt, (bw // 2 - txt.get_width() // 2, 24))
        sub = font_sub.render(subtitle, True, (160, 170, 180))
        surf.blit(sub, (bw // 2 - sub.get_width() // 2, 74))
        return surf

    normal_surf     = make_mode_btn("NORMAL MODE", "Manual enemy tuning", (80, 120, 220))
    dynamic_surf    = make_mode_btn("DYNAMIC MODE", "AI adapts live", (220, 45, 55))
    experiment_surf = make_mode_btn("EXPERIMENT MODE", "Distribution-based test runs", (45, 170, 110))

    gap = 16
    total_w = normal_surf.get_width() + dynamic_surf.get_width() + experiment_surf.get_width() + (gap * 2)
    nx = W // 2 - total_w // 2
    dx = nx + normal_surf.get_width() + gap
    ex = dx + dynamic_surf.get_width() + gap
    by = H // 2 - 38

    normal_rect     = normal_surf.get_rect(topleft=(nx, by))
    dynamic_rect    = dynamic_surf.get_rect(topleft=(dx, by))
    experiment_rect = experiment_surf.get_rect(topleft=(ex, by))

    desc_lines = [
        "Dynamic: adapts every few seconds from your pace.",
        "Experiment: sample enemy parameters from chosen distributions.",
        "HUD auto-enabled. F1 toggles HUD.",
    ]

    fade = 255

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if normal_rect.collidepoint(event.pos):
                    return 'normal'
                if dynamic_rect.collidepoint(event.pos):
                    return 'dynamic'
                if experiment_rect.collidepoint(event.pos):
                    return 'experiment'

        draw_bg(screen, 0, assets, W, H)

        panel = pygame.Surface((760, 300), pygame.SRCALPHA)
        panel.fill((8, 8, 14, 210))
        px = (W - 760) // 2
        py = H // 2 - 120
        screen.blit(panel, (px, py))
        pygame.draw.rect(screen, (60, 60, 80), (px, py, 760, 300), 2, border_radius=4)

        title = font_title.render("SELECT  GAME  MODE", True, (240, 240, 250))
        screen.blit(title, (W // 2 - title.get_width() // 2, py + 16))

        mouse = pygame.mouse.get_pos()
        for rect, surf in [(normal_rect, normal_surf), (dynamic_rect, dynamic_surf), (experiment_rect, experiment_surf)]:
            if rect.collidepoint(mouse):
                hi = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
                hi.fill((255, 255, 255, 22))
                screen.blit(hi, rect.topleft)
            screen.blit(surf, rect.topleft)

        dy2 = by + 140
        for line in desc_lines:
            s = font_sub.render(line, True, (130, 145, 165))
            screen.blit(s, (px + 28, dy2)); dy2 += 17

        hint = font_sub.render("ESC to go back", True, (70, 80, 95))
        screen.blit(hint, (W // 2 - hint.get_width() // 2, py + 278))

        if fade > 0:
            fo = pygame.Surface((W, H)); fo.fill((0,0,0)); fo.set_alpha(fade)
            screen.blit(fo, (0, 0))
            fade = max(0, fade - 12)

        pygame.display.flip()


def draw_experiment_config(screen, clock, assets, exp_mgr, selected_dist):
    """
    Configure which distribution each experiment parameter uses.
    Returns the selected distribution map, or None if canceled.
    """
    W, H = screen.get_size()
    font_title = pygame.font.SysFont('Futura', 28, bold=True)
    font_med = pygame.font.SysFont('Futura', 18)
    font_small = pygame.font.SysFont('Futura', 14)

    params = exp_mgr.parameter_order()
    focus_idx = 0
    fade = 255
    PREVIEW_SAMPLE_COUNT = 10000
    preview_cache = {}
    popup_request = False

    def get_preview_data(param_key, dist_name):
        cache_key = (param_key, dist_name)
        if cache_key in preview_cache:
            return preview_cache[cache_key]

        cfg = exp_mgr.PARAM_CONFIG[param_key]
        samples = exp_mgr.preview_samples(param_key, dist_name, sample_count=PREVIEW_SAMPLE_COUNT)
        values_min = cfg["min"]
        values_max = cfg["max"]
        bins = 24
        counts = [0] * bins
        span = max(1e-9, values_max - values_min)

        for sample in samples:
            index = int(((sample - values_min) / span) * bins)
            index = max(0, min(bins - 1, index))
            counts[index] += 1

        max_count = max(counts) if counts else 1
        default_value = exp_mgr.get_effective_default(param_key)

        data = {
            "cfg": cfg,
            "samples": samples,
            "counts": counts,
            "span": span,
            "max_count": max_count,
            "default_value": default_value,
        }
        preview_cache[cache_key] = data
        return data

    def draw_distribution_preview(surface, rect, param_key, dist_name):
        data = get_preview_data(param_key, dist_name)
        cfg = data["cfg"]
        samples = data["samples"]
        counts = data["counts"]
        span = data["span"]
        max_count = data["max_count"]
        default_value = data["default_value"]

        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        panel.fill((8, 10, 14, 255))
        pygame.draw.rect(panel, (70, 82, 96), (0, 0, rect.width, rect.height), 2, border_radius=6)

        title = font_med.render(f"Distribution Preview: {dist_name.upper()}", True, (245, 245, 250))
        panel.blit(title, (16, 12))

        subtitle = font_small.render(exp_mgr.distribution_explanation(dist_name), True, (215, 220, 230))
        panel.blit(subtitle, (16, 38))

        best_label = font_small.render(
            f"Best distribution suggestion: {cfg['best'].upper()}", True, (180, 220, 180)
        )
        panel.blit(best_label, (16, 56))

        observed_label = font_small.render(
            f"Observed baseline: {default_value:.1f}", True, (230, 240, 255)
        )
        panel.blit(observed_label, (16, 74))

        graph_x = 16
        graph_y = 94
        graph_w = rect.width - 32
        graph_h = rect.height - 130

        pygame.draw.rect(panel, (22, 28, 38), (graph_x, graph_y, graph_w, graph_h), border_radius=4)
        pygame.draw.rect(panel, (58, 68, 82), (graph_x, graph_y, graph_w, graph_h), 1, border_radius=4)

        bar_gap = 2
        bar_w = max(2, (graph_w - (24 - 1) * bar_gap) // 24)
        color = exp_mgr.distribution_label_color(dist_name)

        for i, count in enumerate(counts):
            height_ratio = count / max_count if max_count > 0 else 0.0
            bar_h = int(height_ratio * (graph_h - 18))
            bx = graph_x + i * (bar_w + bar_gap)
            by = graph_y + graph_h - bar_h - 8
            pygame.draw.rect(panel, color, (bx, by, bar_w, bar_h), border_radius=2)

        min_label = font_small.render(str(cfg["min"]), True, (220, 220, 220))
        max_label = font_small.render(str(cfg["max"]), True, (220, 220, 220))
        default_label = font_small.render(f"baseline {default_value:.1f}", True, (245, 245, 245))
        panel.blit(min_label, (graph_x, rect.height - 42))
        panel.blit(max_label, (graph_x + graph_w - max_label.get_width(), rect.height - 42))

        default_x = graph_x + int(((default_value - cfg["min"]) / span) * graph_w)
        pygame.draw.line(panel, (255, 255, 255), (default_x, graph_y), (default_x, graph_y + graph_h), 1)
        panel.blit(default_label, (max(8, min(rect.width - default_label.get_width() - 8, default_x - default_label.get_width() // 2)), graph_y - 22))

        stats_line = font_small.render(
            f"min {min(samples):.1f}   mean {sum(samples)/len(samples):.1f}   max {max(samples):.1f}   samples {len(samples)}",
            True,
            (160, 170, 182),
        )
        panel.blit(stats_line, (16, rect.height - 18))

        surface.blit(panel, rect.topleft)

    def show_distribution_popup(param_key, dist_name):
        popup_w = min(W - 180, 700)
        # popup_w = min(W - 220, 660)
        popup_h = min(H - 120, 520)
        popup_x = max(40, (W - popup_w) // 2 -30)
        popup_rect = pygame.Rect(popup_x, (H - popup_h) // 2, popup_w, popup_h)

        while True:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_p):
                    return None

            draw_bg(screen, 0, assets, W, H)
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 240))
            screen.blit(overlay, (0, 0))

            draw_distribution_preview(screen, popup_rect, param_key, dist_name)

            close_hint = font_small.render("Press P or ESC to close popup", True, (225, 225, 225))
            screen.blit(close_hint, (popup_rect.left + 16, popup_rect.bottom - 28))

            pygame.display.flip()

    popup_active = False

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return dict(selected_dist)
                if event.key == pygame.K_p:
                    popup_request = True
                if event.key == pygame.K_UP:
                    focus_idx = (focus_idx - 1) % len(params)
                if event.key == pygame.K_DOWN:
                    focus_idx = (focus_idx + 1) % len(params)
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    key = params[focus_idx]
                    cfg = exp_mgr.PARAM_CONFIG[key]
                    options = cfg["options"]
                    cur = selected_dist.get(key, cfg["best"])
                    cur_i = options.index(cur)
                    step = -1 if event.key == pygame.K_LEFT else 1
                    selected_dist[key] = options[(cur_i + step) % len(options)]

        draw_bg(screen, 0, assets, W, H)

        panel_w = int(W * 0.82)
        panel_h = int(H * 0.72)
        px = (W - panel_w) // 2
        py = int(H * 0.11)

        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((8, 10, 14, 220))
        screen.blit(panel, (px, py))
        pygame.draw.rect(screen, (45, 170, 110), (px, py, panel_w, panel_h), 2, border_radius=4)

        title = font_title.render("EXPERIMENT MODE SETTINGS", True, (240, 248, 244))
        screen.blit(title, title.get_rect(centerx=W // 2, y=py + 14))

        y = py + 72
        row_h = 46
        for i, key in enumerate(params):
            cfg = exp_mgr.PARAM_CONFIG[key]
            is_focus = (i == focus_idx)
            row_rect = pygame.Rect(px + 24, y, panel_w - 48, row_h - 6)

            if is_focus:
                pygame.draw.rect(screen, (30, 70, 55), row_rect, border_radius=4)
                pygame.draw.rect(screen, (65, 190, 130), row_rect, 1, border_radius=4)

            label = font_med.render(cfg["label"], True, (232, 236, 240))
            screen.blit(label, (row_rect.x + 10, row_rect.y + 10))

            dist = selected_dist.get(key, cfg["best"])
            right = font_med.render(f"{dist.upper()}   (best: {cfg['best']})", True, (160, 220, 192))
            screen.blit(right, (row_rect.right - right.get_width() - 10, row_rect.y + 10))

            y += row_h

        current_key = params[focus_idx]
        current_dist = selected_dist.get(current_key, exp_mgr.PARAM_CONFIG[current_key]["best"])
        graph_rect = pygame.Rect(px + panel_w - 338, py + 70, 300, 250)

        placeholder = pygame.Surface((graph_rect.width, graph_rect.height), pygame.SRCALPHA)
        placeholder.fill((15, 18, 22, 255))
        pygame.draw.rect(placeholder, (58, 68, 82), (0, 0, graph_rect.width, graph_rect.height), 2, border_radius=6)

        p_title = font_med.render("Graph preview popup", True, (245, 245, 250))
        placeholder.blit(p_title, (16, 18))
        p_dist = font_small.render(f"Current distribution: {current_dist.upper()}", True, (200, 220, 200))
        placeholder.blit(p_dist, (16, 48))
        p_best = font_small.render(f"Suggested best: {exp_mgr.PARAM_CONFIG[current_key]['best'].upper()}", True, (180, 235, 180))
        placeholder.blit(p_best, (16, 70))
        p_hint = font_small.render("Press P to open the full graph popup", True, (190, 190, 220))
        placeholder.blit(p_hint, (16, 98))

        screen.blit(placeholder, graph_rect.topleft)
        if popup_request:
            show_distribution_popup(current_key, current_dist)
            popup_request = False

        info_rect = pygame.Rect(px + panel_w - 338, py + 334, 300, 86)
        info_panel = pygame.Surface((info_rect.width, info_rect.height), pygame.SRCALPHA)
        info_panel.fill((12, 16, 24, 225))
        pygame.draw.rect(info_panel, (70, 82, 96), (0, 0, info_rect.width, info_rect.height), 2, border_radius=6)
        info_label = font_med.render("How to read it", True, (240, 244, 248))
        info_panel.blit(info_label, (14, 10))
        help_1 = font_small.render("Bars show how often values appear in sampled runs.", True, (160, 172, 186))
        help_2 = font_small.render("White line marks the default / center value.", True, (160, 172, 186))
        info_panel.blit(help_1, (14, 36))
        info_panel.blit(help_2, (14, 54))
        screen.blit(info_panel, info_rect.topleft)

        hint_lines = [
            "UP/DOWN: select parameter    LEFT/RIGHT: change distribution",
            "P: open popup preview    ENTER: start run    ESC: back",
            "At run start, values are sampled and then fixed for that run.",
        ]
        hy = py + panel_h - 78
        for line in hint_lines:
            hs = font_small.render(line, True, (145, 160, 172))
            screen.blit(hs, (px + 22, hy))
            hy += 18

        if fade > 0:
            fo = pygame.Surface((W, H))
            fo.fill((0, 0, 0))
            fo.set_alpha(fade)
            screen.blit(fo, (0, 0))
            fade = max(0, fade - 12)

        pygame.display.flip()


# ──────────────────────────────────────────────
#  CONFIG PAGE  (Normal Mode only)
# ──────────────────────────────────────────────

def draw_config_page(screen, clock, assets, init_vision_w, init_idle_chance):
    W, H = screen.get_size()
    font_title = pygame.font.SysFont('Futura', 28, bold=True)
    font_med   = pygame.font.SysFont('Futura', 20)
    font_small = pygame.font.SysFont('Futura', 15)

    slider_w = int(W * 0.55)
    cx = W // 2

    slider_vision = Slider(cx - slider_w // 2, int(H * 0.40),
                           slider_w, 60, 400, init_vision_w, step=10,
                           label="Enemy Vision Width")
    slider_idle   = Slider(cx - slider_w // 2, int(H * 0.57),
                           slider_w, 20, 600, init_idle_chance, step=20,
                           label="Enemy Idle Chance  (1 / N)")

    start_img = assets["start_img"]
    play_btn  = button.Button(cx - start_img.get_width() // 2,
                              int(H * 0.73), start_img, 1)
    fade = 255

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None
            slider_vision.handle_event(event)
            slider_idle.handle_event(event)

        draw_bg(screen, 0, assets, W, H)

        panel_w = int(W * 0.70); panel_h = int(H * 0.68)
        panel   = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((8, 8, 12, 205))
        px = (W - panel_w) // 2; py = int(H * 0.13)
        screen.blit(panel, (px, py))
        pygame.draw.rect(screen, (220, 45, 55), (px, py, panel_w, panel_h), 2, border_radius=3)

        t_surf = font_title.render("MISSION  SETTINGS  (Normal Mode)", True, (255, 255, 255))
        screen.blit(t_surf, t_surf.get_rect(centerx=cx, y=py + 18))
        pygame.draw.line(screen, (220, 45, 55), (px + 28, py + 58), (px + panel_w - 28, py + 58), 1)

        slider_vision.draw(screen, font_med)
        slider_idle.draw(screen, font_med)

        h1 = font_small.render("Smaller vision = harder to spot you  |  Higher N = enemies idle less", True, (155, 165, 175))
        h2 = font_small.render("Live tuning:  F2/F3 Vision   F4/F5 Idle   F1 Toggle HUD", True, (110, 120, 130))
        screen.blit(h1, h1.get_rect(centerx=cx, y=int(H * 0.68)))
        screen.blit(h2, h2.get_rect(centerx=cx, y=int(H * 0.71)))

        if play_btn.draw(screen):
            return slider_vision.value, slider_idle.value

        if fade > 0:
            fo = pygame.Surface((W, H)); fo.fill((0,0,0)); fo.set_alpha(fade)
            screen.blit(fo, (0, 0))
            fade = max(0, fade - 12)

        pygame.display.flip()


# ──────────────────────────────────────────────
#  LEVEL INTRO
# ──────────────────────────────────────────────

class LevelIntro:
    FADE_IN = 45; HOLD = 90; FADE_OUT = 55

    def __init__(self):
        self.active = False; self.timer = 0; self.level = 1; self._font = None

    def _get_font(self):
        if self._font is None:
            for name in ['Arial Black', 'Impact', 'Arial', 'Verdana']:
                try:
                    f = pygame.font.SysFont(name, 80, bold=True)
                    f.render("TEST", True, (255,255,255))
                    self._font = f; break
                except Exception: pass
            if self._font is None:
                self._font = pygame.font.Font(None, 80)
        return self._font

    def trigger(self, level):
        self.level = level
        self.timer = self.FADE_IN + self.HOLD + self.FADE_OUT
        self.active = True

    def update_draw(self, screen):
        if not self.active: return
        self.timer -= 1
        if self.timer <= 0: self.active = False; return
        total = self.FADE_IN + self.HOLD + self.FADE_OUT
        elapsed = total - self.timer
        if elapsed < self.FADE_IN:
            alpha = int(255 * elapsed / self.FADE_IN)
        elif elapsed < self.FADE_IN + self.HOLD:
            alpha = 255
        else:
            p = elapsed - self.FADE_IN - self.HOLD
            alpha = int(255 * (1.0 - p / self.FADE_OUT))
        alpha = max(0, min(255, alpha))
        W, H = screen.get_size(); font = self._get_font()
        text = f"LEVEL  {self.level}"
        main_s = font.render(text, True, (255,255,255))
        tw, th = main_s.get_size(); pad = 30; bar_h = 5
        cw = tw + pad*2; ch = th + bar_h + 16
        comp = pygame.Surface((cw, ch), pygame.SRCALPHA)
        comp.blit(font.render(text, True, (10,10,10)), (pad+4, 4))
        comp.blit(main_s, (pad, 0))
        pygame.draw.rect(comp, (220,45,55), (pad, th+8, tw, bar_h))
        comp.set_alpha(alpha)
        screen.blit(comp, (W//2 - cw//2, H//2 - ch//2))


# ──────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Shooting Game")
    clock  = pygame.time.Clock()
    font   = pygame.font.SysFont('Futura', 22)

    assets    = load_assets()
    tile_size = assets["TILE_SIZE"]

    front_back_img = pygame.image.load('assets/img/front_back.png').convert()
    front_back_img = pygame.transform.scale(front_back_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

    entities.inject_static_refs(
        screen=screen, tile_size=tile_size,
        item_boxes=assets["item_boxes"],
        bullet_img=assets["bullet_img"],
        grenade_img=assets["grenade_img"],
    )

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
    game_mode      = None
    game_mode_ref  = {"value": None}
    game_state     = 'menu'
    game_completed = False

    world_data         = load_level_csv(f'assets/level{level}_data.csv', ROWS, COLS)
    player, health_bar = world.process_data(world_data)

    scroll_ref            = {"screen_scroll": 0, "bg_scroll": 0}
    enemy_vision_w_ref    = {"value": ENEMY_VISION_W}
    enemy_vision_h_ref    = {"value": ENEMY_VISION_H}
    enemy_idle_chance_ref = {"value": ENEMY_IDLE_CHANCE}
    enemy_bullet_damage_ref = {"value": 5}

    dynamic_ai = DynamicAI(
        enemy_vision_w_ref,
        enemy_idle_chance_ref,
        enemy_bullet_damage_ref,
        sim,
    )
    experiment_mgr = ExperimentManager(output_dir="experiment_results")
    experiment_selected_dist = experiment_mgr.default_distribution_selection()
    experiment_sampled_values = None
    experiment_report_saved = False

    observed_param_stats = {
        "enemy_vision_w":     {"sum": 0.0, "count": 0},
        "enemy_idle_chance":  {"sum": 0.0, "count": 0},
        "enemy_shoot_cd":     {"sum": 0.0, "count": 0},
        "enemy_speed_mult":   {"sum": 0.0, "count": 0},
        "enemy_health_mult":  {"sum": 0.0, "count": 0},
    }

    def record_observed_param(name, value):
        stats = observed_param_stats.get(name)
        if stats is None:
            return
        stats["sum"] += float(value)
        stats["count"] += 1

    def get_observed_defaults():
        return {
            key: (stats["sum"] / stats["count"] if stats["count"] > 0 else None)
            for key, stats in observed_param_stats.items()
        }

    def apply_observed_defaults():
        experiment_mgr.set_runtime_defaults(get_observed_defaults())

    def _inject():
        entities.inject_game_refs(
            screen=screen, world=world, player=player, sim=sim,
            groups=groups, assets=assets,
            sim_tuning={
                "ENEMY_VISION_W_REF":    enemy_vision_w_ref,
                "ENEMY_VISION_H_REF":    enemy_vision_h_ref,
                "ENEMY_IDLE_CHANCE_REF": enemy_idle_chance_ref,
                "ENEMY_BULLET_DAMAGE_REF": enemy_bullet_damage_ref,
                "GAME_MODE_REF": game_mode_ref,
            },
            screen_scroll_ref=scroll_ref,
        )
        sim.set_player_ref(player)
        dynamic_ai.set_player_ref(player)
        dynamic_ai.set_enemy_group(groups["enemy_group"])

    _inject()

    start_button   = button.Button(SCREEN_WIDTH//2 - 80,  SCREEN_HEIGHT//2 - 110, assets["start_img"],   1)
    exit_button    = button.Button(SCREEN_WIDTH//2 - 80,  SCREEN_HEIGHT//2 + 50,  assets["exit_img"],    1)
    restart_button = button.Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 50,  assets["restart_img"], 1)
    quit_button    = button.Button(SCREEN_WIDTH//2 - 110, SCREEN_HEIGHT//2 + 140, assets["exit_img"],    1)

    moving_left = moving_right = shoot = grenade = grenade_thrown = False
    level_intro = LevelIntro()

    global SIM_SHOW_HUD
    run = True

    while run:
        clock.tick(FPS)

        # ── MENU ──────────────────────────────────────────────────────
        if game_state == 'menu':
            screen.blit(front_back_img, (0, 0))
            if start_button.draw(screen): game_state = 'mode_select'
            if exit_button.draw(screen):  run = False

        # ── MODE SELECT ───────────────────────────────────────────────
        elif game_state == 'mode_select':
            result = draw_mode_select(screen, clock, assets)
            if result is None:
                game_state = 'menu'
            elif result == 'normal':
                game_mode = 'normal'; game_mode_ref["value"] = 'normal'; game_state = 'config'
            elif result == 'dynamic':
                game_mode = 'dynamic'
                game_mode_ref["value"] = 'dynamic'
                enemy_vision_w_ref["value"]    = ENEMY_VISION_W
                enemy_idle_chance_ref["value"] = ENEMY_IDLE_CHANCE
                level = 1; game_completed = False; scroll_ref["bg_scroll"] = 0
                sim.reset(level_started=level)

                world_data = reset_level(groups, ROWS, COLS)
                world_data = load_level_csv(f'assets/level{level}_data.csv', ROWS, COLS)
                world = World()
                inject_world_assets(assets["img_list"], tile_size, groups)
                player, health_bar = world.process_data(world_data)
                _inject()

                # Fresh dynamic AI state
                dynamic_ai.reset_runtime()
                dynamic_ai.reset_speed()

                SIM_SHOW_HUD = True
                level_intro.trigger(level)
                game_state = 'playing'
            elif result == 'experiment':
                game_mode = 'experiment'
                game_mode_ref["value"] = 'experiment'
                apply_observed_defaults()
                game_state = 'experiment_config'

        # ── EXPERIMENT CONFIG ────────────────────────────────────────
        elif game_state == 'experiment_config':
            result = draw_experiment_config(
                screen, clock, assets,
                exp_mgr=experiment_mgr,
                selected_dist=experiment_selected_dist,
            )
            if result is None:
                game_state = 'mode_select'
            else:
                experiment_selected_dist = result
                experiment_sampled_values = experiment_mgr.sample_values(experiment_selected_dist)

                enemy_vision_w_ref["value"] = ENEMY_VISION_W
                enemy_idle_chance_ref["value"] = ENEMY_IDLE_CHANCE

                level = 1
                game_completed = False
                scroll_ref["bg_scroll"] = 0
                sim.reset(level_started=level)

                world_data = reset_level(groups, ROWS, COLS)
                world_data = load_level_csv(f'assets/level{level}_data.csv', ROWS, COLS)
                world = World()
                inject_world_assets(assets["img_list"], tile_size, groups)
                player, health_bar = world.process_data(world_data)
                _inject()

                experiment_mgr.apply_to_refs(
                    experiment_sampled_values,
                    enemy_vision_w_ref,
                    enemy_idle_chance_ref,
                )
                experiment_mgr.apply_to_enemy_group(groups["enemy_group"], experiment_sampled_values)

                dynamic_ai.reset_speed()
                experiment_report_saved = False
                SIM_SHOW_HUD = True
                level_intro.trigger(level)
                game_state = 'playing'

        # ── CONFIG  (Normal Mode) ─────────────────────────────────────
        elif game_state == 'config':
            result = draw_config_page(
                screen, clock, assets,
                init_vision_w=enemy_vision_w_ref["value"],
                init_idle_chance=enemy_idle_chance_ref["value"],
            )
            if result is None:
                game_state = 'mode_select'
            else:
                enemy_vision_w_ref["value"], enemy_idle_chance_ref["value"] = result
                level = 1; game_completed = False; scroll_ref["bg_scroll"] = 0
                sim.reset(level_started=level)

                world_data = reset_level(groups, ROWS, COLS)
                world_data = load_level_csv(f'assets/level{level}_data.csv', ROWS, COLS)
                world = World()
                inject_world_assets(assets["img_list"], tile_size, groups)
                player, health_bar = world.process_data(world_data)
                _inject()

                level_intro.trigger(level)
                game_state = 'playing'

        # ── PLAYING ───────────────────────────────────────────────────
        elif game_state == 'playing':
            draw_bg(screen, scroll_ref["bg_scroll"], assets, SCREEN_WIDTH, SCREEN_HEIGHT)

            sim.tick_trace()

            if game_mode == 'dynamic' and player.alive and not game_completed:
                dynamic_ai.tick(groups["enemy_group"])
            elif game_mode == 'experiment' and experiment_sampled_values and player.alive and not game_completed:
                experiment_mgr.apply_to_enemy_group(groups["enemy_group"], experiment_sampled_values)

            if player.alive and not game_completed and game_mode in ('normal', 'dynamic'):
                record_observed_param("enemy_vision_w", enemy_vision_w_ref["value"])
                record_observed_param("enemy_idle_chance", enemy_idle_chance_ref["value"])
                if game_mode == 'dynamic':
                    record_observed_param("enemy_shoot_cd", dynamic_ai.enemy_shoot_cd)
                    record_observed_param("enemy_speed_mult", dynamic_ai.player_speed_mult)
                    record_observed_param("enemy_health_mult", 1.0)

            world.draw(screen, scroll_ref["screen_scroll"])

            health_bar.draw(player.health)
            draw_text(screen, 'AMMO: ', font, WHITE, 10, 35)
            for x in range(player.ammo):
                screen.blit(assets["bullet_img"], (90 + (x * 10), 40))
            draw_text(screen, 'GRENADES: ', font, WHITE, 10, 60)
            for x in range(player.grenades):
                screen.blit(assets["grenade_img"], (135 + (x * 15), 62))

            if SIM_SHOW_HUD:
                if game_mode == 'dynamic':
                    draw_dynamic_hud(screen, font, sim, dynamic_ai)
                else:
                    draw_sim_hud(screen, font, sim, enemy_vision_w_ref["value"], enemy_idle_chance_ref["value"])

            player.update()
            player.draw()
            for enemy in groups["enemy_group"]:
                enemy.ai(); enemy.update(); enemy.draw()
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
                if shoot: player.shoot()
                elif grenade and not grenade_thrown and player.grenades > 0:
                    g = Grenade(
                        player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),
                        player.rect.top, player.direction,
                    )
                    groups["grenade_group"].add(g)
                    player.grenades -= 1; grenade_thrown = True
                    sim.record_grenade_throw()

                if player.in_air:          player.update_action(2)
                elif moving_left or moving_right: player.update_action(1)
                else:                      player.update_action(0)

                scroll_ref["screen_scroll"], level_complete = player.move(moving_left, moving_right)
                scroll_ref["bg_scroll"] -= scroll_ref["screen_scroll"]

                if level_complete:
                    level += 1; scroll_ref["bg_scroll"] = 0
                    world_data = reset_level(groups, ROWS, COLS)
                    if level <= MAX_LEVELS:
                        world_data = load_level_csv(f'assets/level{level}_data.csv', ROWS, COLS)
                        world = World()
                        inject_world_assets(assets["img_list"], tile_size, groups)
                        player, health_bar = world.process_data(world_data)
                        _inject()
                        if game_mode == 'experiment' and experiment_sampled_values:
                            experiment_mgr.apply_to_refs(
                                experiment_sampled_values,
                                enemy_vision_w_ref,
                                enemy_idle_chance_ref,
                            )
                            experiment_mgr.apply_to_enemy_group(groups["enemy_group"], experiment_sampled_values)
                        level_intro.trigger(level)
                    else:
                        game_completed = True
                        sim.ended_at   = time.time()
                        sim.save_outputs_once(final_level=MAX_LEVELS, completed=True)

            else:
                scroll_ref["screen_scroll"] = 0
                if sim.ended_at is None: sim.ended_at = time.time()
                sim.save_outputs_once(final_level=min(level, MAX_LEVELS), completed=game_completed)
                if game_mode == 'experiment' and (not experiment_report_saved) and experiment_sampled_values:
                    experiment_mgr.save_experiment_report(
                        sim=sim,
                        final_level=min(level, MAX_LEVELS),
                        completed=game_completed,
                        distribution_selection=experiment_selected_dist,
                        sampled_values=experiment_sampled_values,
                    )
                    experiment_report_saved = True

                report_bottom_y = draw_sim_report(
                    screen, font, sim,
                    completed=game_completed,
                    final_level=min(level, MAX_LEVELS),
                    enemy_vision_w=enemy_vision_w_ref["value"],
                    enemy_idle_chance=enemy_idle_chance_ref["value"],
                    screen_w=SCREEN_WIDTH, screen_h=SCREEN_HEIGHT,
                )

                btn_y = min(report_bottom_y + 25, SCREEN_HEIGHT - 80)
                restart_button.rect.topleft = (SCREEN_WIDTH//2 - restart_button.rect.width - 15, btn_y)
                quit_button.rect.topleft    = (SCREEN_WIDTH//2 + 15, btn_y)

                if restart_button.draw(screen):
                    experiment_sampled_values = None
                    experiment_report_saved = False
                    game_state = 'mode_select'
                if quit_button.draw(screen):    run = False

        # ── EVENTS ────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT: run = False

            if event.type == pygame.KEYDOWN:
                if game_state == 'playing':
                    if event.key == pygame.K_a:     moving_left  = True
                    if event.key == pygame.K_d:     moving_right = True
                    if event.key == pygame.K_q:     grenade      = True
                    if event.key == pygame.K_SPACE and player.alive: shoot = True
                    if event.key == pygame.K_w and player.alive: player.jump = True

                    # Dynamic mode speed control
                    if game_mode == 'dynamic':
                        if event.key == pygame.K_F6: dynamic_ai.speed_down()
                        if event.key == pygame.K_F7: dynamic_ai.speed_up()
                        if event.key == pygame.K_F8: dynamic_ai.reset_speed()

                    # Normal mode live tuning
                    if game_mode == 'normal':
                        if event.key == pygame.K_F2: enemy_vision_w_ref["value"]    = max(60,  enemy_vision_w_ref["value"] - 20)
                        if event.key == pygame.K_F3: enemy_vision_w_ref["value"]    = min(400, enemy_vision_w_ref["value"] + 20)
                        if event.key == pygame.K_F4: enemy_idle_chance_ref["value"] = max(20,  enemy_idle_chance_ref["value"] - 20)
                        if event.key == pygame.K_F5: enemy_idle_chance_ref["value"] = min(600, enemy_idle_chance_ref["value"] + 20)

                if event.key == pygame.K_ESCAPE: run = False
                if event.key == pygame.K_F1: SIM_SHOW_HUD = not SIM_SHOW_HUD

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:     moving_left    = False
                if event.key == pygame.K_d:     moving_right   = False
                if event.key == pygame.K_SPACE: shoot          = False
                if event.key == pygame.K_q:
                    grenade = False; grenade_thrown = False

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()