import pygame
import time

import button

from settings import *
from assets_loader import load_assets
from simulation_stats import SimulationStats
from ui_sim import draw_text, draw_bg, draw_sim_hud, draw_sim_report

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
#  CONFIG PAGE
# ──────────────────────────────────────────────

def draw_config_page(screen, clock, assets, init_vision_w, init_idle_chance):
    """
    Settings page between menu and game.
    Background = game parallax bg.
    PLAY button = the same start_img used on the main menu.
    Returns (vision_w, idle_chance) or None (ESC → back to menu).
    """
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

    # Use the real start_img button
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

        panel_w = int(W * 0.70)
        panel_h = int(H * 0.68)
        panel   = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((8, 8, 12, 205))
        px = (W - panel_w) // 2
        py = int(H * 0.13)
        screen.blit(panel, (px, py))
        pygame.draw.rect(screen, (220, 45, 55), (px, py, panel_w, panel_h), 2, border_radius=3)

        t_surf = font_title.render("MISSION  SETTINGS", True, (255, 255, 255))
        screen.blit(t_surf, t_surf.get_rect(centerx=cx, y=py + 18))
        pygame.draw.line(screen, (220, 45, 55),
                         (px + 28, py + 58), (px + panel_w - 28, py + 58), 1)

        slider_vision.draw(screen, font_med)
        slider_idle.draw(screen, font_med)

        h1 = font_small.render(
            "Smaller vision = enemies harder to spot you      |      Higher N = enemies idle less often",
            True, (155, 165, 175))
        h2 = font_small.render(
            "Live tuning during gameplay:   F2 / F3  Vision      F4 / F5  Idle      F1  Toggle HUD",
            True, (110, 120, 130))
        screen.blit(h1, h1.get_rect(centerx=cx, y=int(H * 0.68)))
        screen.blit(h2, h2.get_rect(centerx=cx, y=int(H * 0.71)))

        if play_btn.draw(screen):
            return slider_vision.value, slider_idle.value

        if fade > 0:
            fo = pygame.Surface((W, H))
            fo.fill((0, 0, 0))
            fo.set_alpha(fade)
            screen.blit(fo, (0, 0))
            fade = max(0, fade - 12)

        pygame.display.flip()


# ──────────────────────────────────────────────
#  LEVEL INTRO FLOATING TEXT
# ──────────────────────────────────────────────

class LevelIntro:
    FADE_IN  = 45
    HOLD     = 90
    FADE_OUT = 55

    def __init__(self):
        self.active = False
        self.timer  = 0
        self.level  = 1
        self._font  = None

    def _get_font(self):
        if self._font is None:
            for name in ['Arial Black', 'Impact', 'Arial', 'Verdana']:
                try:
                    f = pygame.font.SysFont(name, 80, bold=True)
                    f.render("TEST", True, (255, 255, 255))
                    self._font = f
                    break
                except Exception:
                    pass
            if self._font is None:
                self._font = pygame.font.Font(None, 80)
        return self._font

    def trigger(self, level: int):
        self.level  = level
        self.timer  = self.FADE_IN + self.HOLD + self.FADE_OUT
        self.active = True

    def update_draw(self, screen: pygame.Surface):
        if not self.active:
            return
        self.timer -= 1
        if self.timer <= 0:
            self.active = False
            return

        total   = self.FADE_IN + self.HOLD + self.FADE_OUT
        elapsed = total - self.timer
        if elapsed < self.FADE_IN:
            alpha = int(255 * elapsed / self.FADE_IN)
        elif elapsed < self.FADE_IN + self.HOLD:
            alpha = 255
        else:
            p     = elapsed - self.FADE_IN - self.HOLD
            alpha = int(255 * (1.0 - p / self.FADE_OUT))
        alpha = max(0, min(255, alpha))

        W, H   = screen.get_size()
        font   = self._get_font()
        text   = f"LEVEL  {self.level}"
        main_s = font.render(text, True, (255, 255, 255))
        tw, th = main_s.get_size()
        pad    = 30
        bar_h  = 5
        cw     = tw + pad * 2
        ch     = th + bar_h + 16

        comp   = pygame.Surface((cw, ch), pygame.SRCALPHA)
        shadow = font.render(text, True, (10, 10, 10))
        comp.blit(shadow, (pad + 4, 4))
        comp.blit(main_s, (pad, 0))
        pygame.draw.rect(comp, (220, 45, 55), (pad, th + 8, tw, bar_h))
        comp.set_alpha(alpha)
        screen.blit(comp, (W // 2 - cw // 2, H // 2 - ch // 2))


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