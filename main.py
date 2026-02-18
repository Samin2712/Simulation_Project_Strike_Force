import pygame
import time

import button

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