# menu.py  —  STRIKE FORCE  Main Menu  (title fixed to match HTML look)
# ─────────────────────────────────────────────────────────────────────────────
import pygame
import math
import random
import sys

# ── palette (matching the HTML screenshot) ────────────────────────────────────
BG_COLOR  = (10,  10,  12)      # near-black background
ACCENT    = (220, 45,  55)      # red
ACCENT_HI = (255, 80,  90)
ACCENT_LO = (140, 18,  26)
SILVER    = (200, 210, 220)
MUTED     = (120, 130, 140)
WHITE     = (255, 255, 255)
BLACK     = (0,   0,   0)
GRID_COL  = (220, 45, 55)       # grid lines — faint red


# ─────────────────────────────────────────────────────────────────────────────
#  BACKGROUND  — solid dark + grid + red radial glow behind title
# ─────────────────────────────────────────────────────────────────────────────

def _make_bg(W, H):
    surf = pygame.Surface((W, H))
    surf.fill(BG_COLOR)

    # faint grid
    grid = pygame.Surface((W, H), pygame.SRCALPHA)
    step = 46
    for x in range(0, W, step):
        pygame.draw.line(grid, (*GRID_COL, 18), (x, 0), (x, H))
    for y in range(0, H, step):
        pygame.draw.line(grid, (*GRID_COL, 18), (0, y), (W, y))
    surf.blit(grid, (0, 0))

    # red radial glow centred slightly above-centre (behind title)
    glow = pygame.Surface((W, H), pygame.SRCALPHA)
    cx, cy = W // 2, int(H * 0.32)
    max_rad = int(min(W, H) * 0.75)
    for rad in range(max_rad, 0, -6):
        t = rad / max_rad
        a = int(42 * (1 - t) ** 2.2)
        pygame.draw.circle(glow, (180, 20, 25, a), (cx, cy), rad)
    surf.blit(glow, (0, 0))

    return surf


def _make_vignette(W, H):
    """Strong dark vignette on all 4 edges."""
    s  = pygame.Surface((W, H), pygame.SRCALPHA)
    cx, cy = W // 2, H // 2
    mr = int(math.hypot(cx, cy))
    for i in range(35):
        t = i / 35
        r_now = int(mr * (0.50 + 0.50 * t))
        alpha = int(200 * t ** 2.0)
        pygame.draw.circle(s, (6, 6, 8, alpha), (cx, cy), r_now, 16)
    return s


# ─────────────────────────────────────────────────────────────────────────────
#  TITLE  — simple, like HTML (thin stroke + shadow + white)
#          IMPORTANT: size uses min(W,H) + clamp (prevents giant title)
# ─────────────────────────────────────────────────────────────────────────────

def _make_title_font(size=108):
    for name in ['Impact', 'Arial Black', 'Arial']:
        try:
            return pygame.font.SysFont(name, size, bold=True)
        except Exception:
            pass
    return pygame.font.Font(None, size)


def _render_title(font):
    TEXT = "STRIKE FORCE"
    pad = 12

    main = font.render(TEXT, True, WHITE)
    tw, th = main.get_size()

    canvas = pygame.Surface((tw + pad*2 + 12, th + pad*2 + 12), pygame.SRCALPHA)

    def blit_text(x, y, col, a=255):
        s = font.render(TEXT, True, col)
        if a != 255:
            s.set_alpha(a)
        canvas.blit(s, (x, y))

    x0 = pad
    y0 = pad

    # thin black outline (stroke) like HTML
    outline = 2
    for dx, dy in [(-outline,0),(outline,0),(0,-outline),(0,outline),
                   (-outline,-outline),(outline,-outline),(-outline,outline),(outline,outline)]:
        blit_text(x0 + dx, y0 + dy, (0, 0, 0), 220)

    # drop shadow
    blit_text(x0 + 3, y0 + 3, (0, 0, 0), 140)

    # main white text
    canvas.blit(main, (x0, y0))
    return canvas


# ─────────────────────────────────────────────────────────────────────────────
#  PARTICLES  (small red dots scattered around)
# ─────────────────────────────────────────────────────────────────────────────

class _Particle:
    def __init__(self, W, H):
        self.W = W; self.H = H
        self.x  = random.uniform(0, W)
        self.y  = random.uniform(0, H)
        self.vx = random.uniform(-0.20, 0.20)
        self.vy = random.uniform(-0.20, 0.20)
        self.r  = random.uniform(1.0, 2.2)
        self.a  = random.randint(40, 120)
        self.red = random.random() < 0.40

    def update(self):
        self.x = (self.x + self.vx) % self.W
        self.y = (self.y + self.vy) % self.H

    def draw(self, surf):
        col = ACCENT if self.red else (80, 90, 100)
        ir  = max(1, int(self.r))
        s   = pygame.Surface((ir*2+2, ir*2+2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*col, self.a), (ir+1, ir+1), ir)
        surf.blit(s, (int(self.x)-ir-1, int(self.y)-ir-1))


# ─────────────────────────────────────────────────────────────────────────────
#  CORNER BRACKETS
# ─────────────────────────────────────────────────────────────────────────────

def _draw_corner_brackets(surf, x, y, w, h, col=ACCENT, sz=28, th=2):
    # top-left
    pygame.draw.line(surf, col, (x,      y+sz),   (x,    y),    th)
    pygame.draw.line(surf, col, (x,      y),      (x+sz, y),    th)
    # top-right
    pygame.draw.line(surf, col, (x+w-sz, y),      (x+w,  y),    th)
    pygame.draw.line(surf, col, (x+w,    y),      (x+w,  y+sz), th)
    # bottom-left
    pygame.draw.line(surf, col, (x,      y+h-sz), (x,    y+h),  th)
    pygame.draw.line(surf, col, (x,      y+h),    (x+sz, y+h),  th)
    # bottom-right
    pygame.draw.line(surf, col, (x+w-sz, y+h),    (x+w,  y+h),  th)
    pygame.draw.line(surf, col, (x+w,    y+h),    (x+w,  y+h-sz), th)


# ─────────────────────────────────────────────────────────────────────────────
#  BUTTON
# ─────────────────────────────────────────────────────────────────────────────

class _Button:
    def __init__(self, cx, y, w, h, label, primary=True):
        self.rect = pygame.Rect(0, 0, w, h)
        self.rect.centerx = cx
        self.rect.y = y
        self.label   = label
        self.primary = primary
        self._ht     = 0.0
        self._flash  = 0.0
        self._down   = False
        self._font   = None

    def _get_font(self):
        if not self._font:
            for n in ['Impact', 'Arial Black', 'Arial']:
                try:
                    self._font = pygame.font.SysFont(n, 20, bold=True)
                    break
                except:
                    pass
            if not self._font:
                self._font = pygame.font.Font(None, 24)
        return self._font

    def update(self, mx, my):
        h = self.rect.collidepoint(mx, my)
        self._ht += ((1.0 if h else 0.0) - self._ht) * 0.14
        if self._flash > 0:
            self._flash = max(0.0, self._flash - 0.08)

    def draw(self, surf):
        ht = self._ht
        r  = self.rect.inflate(int(ht*6), int(ht*4))
        r.center = self.rect.center

        if self.primary:
            base_r = int(ACCENT_LO[0] + (ACCENT[0]-ACCENT_LO[0]) * 0.6 + 30*ht)
            base_g = int(ACCENT_LO[1] + (ACCENT[1]-ACCENT_LO[1]) * 0.6)
            base_b = int(ACCENT_LO[2] + (ACCENT[2]-ACCENT_LO[2]) * 0.6)
            fill   = (min(255, base_r), base_g, base_b)
            pygame.draw.rect(surf, fill, r, border_radius=4)

            hl = pygame.Surface((r.width, 2), pygame.SRCALPHA)
            hl.fill((255, 255, 255, 40))
            surf.blit(hl, (r.x, r.y))
        else:
            fill_a = int(60 + 40*ht)
            bs = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
            bs.fill((30, 32, 36, fill_a))
            surf.blit(bs, r.topleft)

            bd = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
            pygame.draw.rect(bd, (*MUTED, int(100+80*ht)), bd.get_rect(),
                             width=1, border_radius=4)
            surf.blit(bd, r.topleft)

        if self._flash > 0:
            fs = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
            pygame.draw.rect(fs, (255, 255, 255, int(self._flash*60)),
                             fs.get_rect(), border_radius=4)
            surf.blit(fs, r.topleft)

        lbl = "  ".join(self.label)
        ts  = self._get_font().render(lbl, True, WHITE)
        surf.blit(ts, ts.get_rect(center=r.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and not self._down:
                self._down = True
                self._flash = 1.0
                return True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._down = False
        return False


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN ENTRY
# ─────────────────────────────────────────────────────────────────────────────

def show_menu(screen, clock):
    """Returns 'start' or 'quit'."""
    W, H = screen.get_size()

    # IMPORTANT: title size is based on min(W,H) and clamped (matches HTML feel)
    base = min(W, H)
    title_size = max(72, min(118, int(base * 0.17)))
    title_font = _make_title_font(title_size)

    try:
        badge_font  = pygame.font.SysFont('Arial', 12, bold=True)
        sub_font    = pygame.font.SysFont('Arial', 13)
        footer_font = pygame.font.SysFont('Arial', 12)
    except:
        badge_font = sub_font = footer_font = pygame.font.Font(None, 16)

    # pre-bake
    bg       = _make_bg(W, H)
    vignette = _make_vignette(W, H)
    title_s  = _render_title(title_font)

    # particles
    parts  = [_Particle(W, H) for _ in range(60)]
    p_surf = pygame.Surface((W, H), pygame.SRCALPHA)

    # layout
    cx        = W // 2
    title_y   = int(H * 0.22)   # HTML-like placement
    panel_top = int(H * 0.56)

    bw = int(W * 0.56)
    bh = 58
    b_start = _Button(cx, panel_top,       bw, bh, "START GAME", primary=True)
    b_quit  = _Button(cx, panel_top + 74,  bw, bh, "QUIT",       primary=False)

    # corner brackets
    bracket_margin = 18
    bk_x = bracket_margin
    bk_y = bracket_margin
    bk_w = W - bracket_margin*2
    bk_h = H - bracket_margin*2

    diamond_y = int(H * 0.52)

    # glitch (optional, kept)
    glitch_t  = 0.0
    glitch_on = False
    glitch_ox = 0

    # fade-in
    fade = 255

    while True:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if b_start.handle_event(event):
                return 'start'
            if b_quit.handle_event(event):
                return 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return 'start'
                if event.key == pygame.K_ESCAPE:
                    return 'quit'

        mx, my = pygame.mouse.get_pos()
        for p in parts:
            p.update()
        b_start.update(mx, my)
        b_quit.update(mx, my)

        # glitch timing
        glitch_t += dt / 1000.0
        if not glitch_on and glitch_t > random.uniform(5, 11):
            glitch_on = True
            glitch_t = 0.0
            glitch_ox = random.choice([-4, -3, 3, 4])
        if glitch_on:
            glitch_t += 0.05
            if glitch_t > 0.08:
                glitch_on = False
                glitch_t = 0.0
                glitch_ox = 0

        # ── DRAW ──────────────────────────────────────────────────────────
        screen.blit(bg, (0, 0))

        p_surf.fill((0, 0, 0, 0))
        for p in parts:
            p.draw(p_surf)
        screen.blit(p_surf, (0, 0))

        screen.blit(vignette, (0, 0))

        _draw_corner_brackets(screen, bk_x, bk_y, bk_w, bk_h, col=ACCENT, sz=32, th=2)

        # badge
        badge_txt = "E L I T E   O P E R A T I O N S   D I V I S I O N"
        badge_s   = badge_font.render(badge_txt, True, ACCENT)
        bw2 = badge_s.get_width() + 20
        bh2 = badge_s.get_height() + 10
        badge_r = pygame.Rect(0, 0, bw2, bh2)
        badge_r.centerx = cx
        badge_r.y = title_y - bh2 - 10
        badge_box = pygame.Surface((bw2, bh2), pygame.SRCALPHA)
        pygame.draw.rect(badge_box, (*ACCENT, 160), badge_box.get_rect(), width=1)
        screen.blit(badge_box, badge_r.topleft)
        screen.blit(badge_s, badge_s.get_rect(center=badge_r.center))

        # glitch ghost (subtle)
        if glitch_on:
            gs = title_font.render("STRIKE FORCE", True, (200, 35, 40))
            gs.set_alpha(55)
            gr = gs.get_rect(centerx=cx + glitch_ox,
                             centery=title_y + title_s.get_height() // 2 - 6)
            screen.set_clip(pygame.Rect(gr.x, gr.y + 18, gr.width, 18))
            screen.blit(gs, gr)
            screen.set_clip(None)

        # title
        screen.blit(title_s, title_s.get_rect(centerx=cx, y=title_y))

        # subtitle
        sub_txt = "T A C T I C A L   C O M B A T   S I M U L A T I O N"
        sub_s   = sub_font.render(sub_txt, True, MUTED)
        sub_s.set_alpha(200)
        screen.blit(sub_s, sub_s.get_rect(centerx=cx,
                                          y=title_y + title_s.get_height() - 6))

        # diamond
        try:
            dia_font = pygame.font.SysFont('Arial', 22)
        except:
            dia_font = pygame.font.Font(None, 26)
        dia_s = dia_font.render("◆", True, ACCENT)
        dia_s.set_alpha(220)
        screen.blit(dia_s, dia_s.get_rect(centerx=cx, centery=diamond_y))

        # buttons
        b_start.draw(screen)
        b_quit.draw(screen)

        # footer
        ver_s = footer_font.render("V1.0.0 — BUILD 2025", True, MUTED)
        ver_s.set_alpha(140)
        screen.blit(ver_s, (W - ver_s.get_width() - 38, H - 38))

        # fade in
        if fade > 0:
            fo = pygame.Surface((W, H))
            fo.fill(BLACK)
            fo.set_alpha(fade)
            screen.blit(fo, (0, 0))
            fade = max(0, fade - 7)

        pygame.display.flip()