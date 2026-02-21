# ui_sim.py
import pygame
from settings import WHITE

def draw_text(screen, text, font, color, x, y):
    img = font.render(str(text), True, color)
    screen.blit(img, (x, y))

def draw_bg(screen, bg_scroll, assets, screen_w, screen_h):
    # Always draw full-screen sky first (no gaps)
    screen.blit(assets["sky_img"], (0, 0))

    mountain = assets["mountain_img"]
    pine1 = assets["pine1_img"]
    pine2 = assets["pine2_img"]

    # parallax repeat width (use each layer's width)
    for x in range(5):
        screen.blit(mountain, ((x * mountain.get_width()) - bg_scroll * 0.6,
                               screen_h - mountain.get_height() - 300))
        screen.blit(pine1, ((x * pine1.get_width()) - bg_scroll * 0.7,
                            screen_h - pine1.get_height() - 150))
        screen.blit(pine2, ((x * pine2.get_width()) - bg_scroll * 0.8,
                            screen_h - pine2.get_height()))

def draw_sim_hud(screen, font, sim, enemy_vision_w, enemy_idle_chance):
    # small readable HUD (only when enabled)
    panel = pygame.Surface((420, 150), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 120))
    screen.blit(panel, (10, 90))

    x = 20
    y = 100
    draw_text(screen, f"SIM HUD | Run #{sim.run_id}", font, WHITE, x, y); y += 22
    draw_text(screen, f"Time: {sim.survival_time():.1f}s   Kills: {sim.kills_player}", font, WHITE, x, y); y += 22
    draw_text(screen, f"Shots: {sim.shots_fired_player}  Hits: {sim.hits_player}  Acc: {sim.accuracy_player():.1f}%", font, WHITE, x, y); y += 22
    draw_text(screen, f"Grenades: {sim.grenades_thrown}  G-Kills: {sim.grenade_kills}", font, WHITE, x, y); y += 22
    draw_text(screen, f"EnemyVisionW: {enemy_vision_w}   IdleChance: 1/{enemy_idle_chance}", font, WHITE, x, y); y += 22
    draw_text(screen, "F1 HUD  F2/F3 Vision  F4/F5 Idle", font, WHITE, x, y)

def draw_sim_report(screen, font, sim, completed, final_level, enemy_vision_w, enemy_idle_chance,
                    screen_w, screen_h):
    """
    Draws report and RETURNS bottom Y coordinate of the last text line.
    """
    overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    screen.blit(overlay, (0, 0))

    panel_w = int(screen_w * 0.74)
    panel_h = int(screen_h * 0.60)
    panel_x = (screen_w - panel_w) // 2
    panel_y = (screen_h - panel_h) // 2 - 40

    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((20, 20, 20, 200))
    screen.blit(panel, (panel_x, panel_y))

    title = "SIMULATION REPORT (COMPLETED)" if completed else "SIMULATION REPORT (GAME OVER)"

    x = panel_x + 24
    y = panel_y + 20

    draw_text(screen, title, font, WHITE, x, y)
    y += 40

    lines = [
        f"Run ID: {sim.run_id}",
        f"Level started: {sim.level_started}    Final level: {final_level}",
        f"Survival time: {sim.survival_time():.2f} seconds",
        f"Kills: {sim.kills_player}",
        f"Shots fired: {sim.shots_fired_player}   Hits: {sim.hits_player}   Acc: {sim.accuracy_player():.1f}%",
        f"Damage done: {sim.damage_done_by_player}   Damage taken: {sim.damage_taken_by_player}",
        f"Grenades thrown: {sim.grenades_thrown}   Grenade kills: {sim.grenade_kills}",
        f"Enemy vision width: {enemy_vision_w}   Enemy idle chance: 1/{enemy_idle_chance}",
        "Saved: simulation_results/runs.csv and simulation_results/path_run_<id>.csv"
    ]

    for line in lines:
        draw_text(screen, line, font, WHITE, x, y)
        y += 28

    return y