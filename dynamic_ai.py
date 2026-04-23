# # dynamic_ai.py
# """
# Dynamic AI Adaptation Engine
# Watches player behaviour every N seconds and adjusts enemy parameters in real-time.

# Tracked signals:
#   - kill_rate       : kills per minute
#   - accuracy        : shot accuracy %
#   - damage_taken    : damage received per minute
#   - movement_speed  : estimated via position trace variance
#   - grenade_use     : grenades thrown per minute

# Outputs (all stored as mutable dicts so entities.py refs stay valid):
#   - ENEMY_VISION_W_REF   : enemy horizontal vision width
#   - ENEMY_IDLE_CHANCE_REF: 1/N idle probability denominator
#   - enemy_shoot_cd       : enemy shoot cooldown frames (written directly)
#   - player speed         : adjusted via player.speed
# """

# import math
# import time


# # ── tuning constants ─────────────────────────────────────────────────────────
# EVAL_INTERVAL   = 8.0    # seconds between adaptation ticks

# VISION_MIN      = 80
# VISION_MAX      = 380
# VISION_STEP     = 20

# IDLE_MIN        = 40
# IDLE_MAX        = 500
# IDLE_STEP       = 40

# SHOOT_CD_MIN    = 30     # fastest enemy fire rate (frames)
# SHOOT_CD_MAX    = 90     # slowest enemy fire rate
# SHOOT_CD_STEP   = 10

# # thresholds
# HIGH_KPM        = 1.5    # kills/min that counts as "aggressive"
# LOW_KPM         = 0.3
# HIGH_ACC        = 60.0   # accuracy % that counts as "sharp shooter"
# LOW_ACC         = 20.0
# HIGH_DMG_TAKEN  = 25.0   # damage/min that counts as "taking a beating"


# class DynamicAI:
#     def __init__(self, vision_ref, idle_ref, sim):
#         """
#         vision_ref  : {"value": int}  – shared dict with entities.py
#         idle_ref    : {"value": int}  – shared dict with entities.py
#         sim         : SimulationStats instance
#         """
#         self.vision_ref = vision_ref
#         self.idle_ref   = idle_ref
#         self.sim        = sim

#         # enemy shoot cooldown — we store it here and patch enemy objects each tick
#         self.enemy_shoot_cd = 60   # default

#         # player speed multiplier (applied to player.speed)
#         self._player_ref     = None
#         self._base_speed     = 5
#         self.player_speed_mult = 1.0   # 1.0 = normal, range 0.5 – 2.0

#         # internal bookmarks for delta calculations
#         self._last_eval_time      = time.time()
#         self._last_kills          = 0
#         self._last_shots          = 0
#         self._last_hits           = 0
#         self._last_damage_taken   = 0
#         self._last_grenades       = 0

#         # for display
#         self.adaptation_level     = 0    # –5 … +5  (pos = harder, neg = easier)
#         self.last_event_log       = []   # list of short strings shown in HUD

#         # player position history for movement estimation
#         self._pos_history         = []

#     def set_player_ref(self, player):
#         self._player_ref = player
#         self._base_speed = player.speed

#     def set_enemy_group(self, enemy_group):
#         self._enemy_group = enemy_group

#     # ── called every frame ───────────────────────────────────────────────────

#     def tick(self, enemy_group):
#         """Call once per game frame."""
#         now = time.time()

#         # record position for movement analysis
#         if self._player_ref:
#             self._pos_history.append(
#                 (now, self._player_ref.rect.centerx, self._player_ref.rect.centery)
#             )
#             # keep only last 10 s
#             cutoff = now - 10
#             self._pos_history = [(t, x, y) for t, x, y in self._pos_history if t >= cutoff]

#         if now - self._last_eval_time >= EVAL_INTERVAL:
#             self._evaluate(now, enemy_group)
#             self._last_eval_time = now

#     # ── internal evaluation ──────────────────────────────────────────────────

#     def _evaluate(self, now, enemy_group):
#         dt_min = EVAL_INTERVAL / 60.0   # interval in minutes

#         # delta stats over the interval
#         kills_delta    = self.sim.kills_player        - self._last_kills
#         shots_delta    = self.sim.shots_fired_player  - self._last_shots
#         hits_delta     = self.sim.hits_player         - self._last_hits
#         dmg_delta      = self.sim.damage_taken_by_player - self._last_damage_taken
#         nade_delta     = self.sim.grenades_thrown     - self._last_grenades

#         # rates
#         kpm   = kills_delta  / dt_min
#         dpm   = dmg_delta    / dt_min
#         acc   = (hits_delta / shots_delta * 100) if shots_delta > 0 else self.sim.accuracy_player()
#         npm   = nade_delta   / dt_min

#         # movement speed estimate (pixels/sec average)
#         move_speed = self._estimate_movement()

#         # save bookmarks
#         self._last_kills        = self.sim.kills_player
#         self._last_shots        = self.sim.shots_fired_player
#         self._last_hits         = self.sim.hits_player
#         self._last_damage_taken = self.sim.damage_taken_by_player
#         self._last_grenades     = self.sim.grenades_thrown

#         events = []
#         delta  = 0   # net adaptation direction this tick (+1 harder, -1 easier)

#         # ── RULE SET ─────────────────────────────────────────────────────────

#         # 1. High kill rate → enemies see further, alert faster
#         if kpm > HIGH_KPM:
#             self._adjust_vision(+VISION_STEP)
#             self._adjust_idle(-IDLE_STEP)      # idle less = more alert
#             events.append(f"High KPM {kpm:.1f} → vision↑ alert↑")
#             delta += 1

#         # 2. Low kill rate + not taking much damage → player hiding/camping
#         elif kpm < LOW_KPM and dpm < HIGH_DMG_TAKEN:
#             self._adjust_vision(+VISION_STEP)  # enemies patrol wider
#             self._adjust_idle(-IDLE_STEP)
#             events.append(f"Low KPM {kpm:.1f} → enemies search harder")
#             delta += 1

#         # 3. Player is a sharpshooter → enemies faster fire rate
#         if acc > HIGH_ACC and shots_delta >= 3:
#             self._adjust_shoot_cd(-SHOOT_CD_STEP)
#             events.append(f"High acc {acc:.0f}% → enemies fire faster")
#             delta += 1

#         # 4. Player is missing a lot → give them a tiny break
#         elif acc < LOW_ACC and shots_delta >= 5:
#             self._adjust_shoot_cd(+SHOOT_CD_STEP)
#             self._adjust_vision(-VISION_STEP)
#             events.append(f"Low acc {acc:.0f}% → enemies ease off")
#             delta -= 1

#         # 5. Player taking lots of damage → tone down enemies a bit
#         if dpm > HIGH_DMG_TAKEN * 3:
#             self._adjust_vision(-VISION_STEP)
#             self._adjust_shoot_cd(+SHOOT_CD_STEP)
#             events.append(f"High dmg taken {dpm:.0f}/min → enemies ease off")
#             delta -= 1

#         # 6. Heavy grenade use → enemies more spread out (idle less)
#         if npm >= 0.5:
#             self._adjust_idle(-IDLE_STEP)
#             events.append(f"Grenade spam → enemies spread out")
#             delta += 1

#         # 7. Player barely moving → enemies widen patrol
#         if move_speed < 30:
#             self._adjust_idle(-IDLE_STEP * 2)
#             events.append("Player stationary → enemies search")
#             delta += 1

#         # ── apply shoot CD to all live enemies ───────────────────────────────
#         for enemy in enemy_group:
#             if enemy.alive:
#                 enemy._dynamic_shoot_cd = self.enemy_shoot_cd

#         # ── update adaptation level ───────────────────────────────────────────
#         self.adaptation_level = max(-5, min(5, self.adaptation_level + delta))

#         # keep last 3 events for HUD
#         self.last_event_log = events[-3:] if events else ["Monitoring…"]

#     # ── adjusters ────────────────────────────────────────────────────────────

#     def _adjust_vision(self, step):
#         v = self.vision_ref["value"] + step
#         self.vision_ref["value"] = max(VISION_MIN, min(VISION_MAX, v))

#     def _adjust_idle(self, step):
#         v = self.idle_ref["value"] + step
#         self.idle_ref["value"] = max(IDLE_MIN, min(IDLE_MAX, v))

#     def _adjust_shoot_cd(self, step):
#         self.enemy_shoot_cd = max(SHOOT_CD_MIN, min(SHOOT_CD_MAX, self.enemy_shoot_cd + step))

#     def _estimate_movement(self):
#         if len(self._pos_history) < 2:
#             return 0
#         total_dist = 0
#         for i in range(1, len(self._pos_history)):
#             t0, x0, y0 = self._pos_history[i - 1]
#             t1, x1, y1 = self._pos_history[i]
#             total_dist += math.hypot(x1 - x0, y1 - y0)
#         elapsed = self._pos_history[-1][0] - self._pos_history[0][0]
#         return total_dist / elapsed if elapsed > 0 else 0

#     # ── player speed control ─────────────────────────────────────────────────

#     def set_player_speed_mult(self, mult):
#         """mult: 0.5 – 2.0"""
#         self.player_speed_mult = max(0.5, min(2.0, mult))
#         if self._player_ref:
#             self._player_ref.speed = int(round(self._base_speed * self.player_speed_mult))

#     def speed_up(self):
#         self.set_player_speed_mult(self.player_speed_mult + 0.25)

#     def speed_down(self):
#         self.set_player_speed_mult(self.player_speed_mult - 0.25)

#     def reset_speed(self):
#         self.set_player_speed_mult(1.0)

#     # ── HUD helpers ──────────────────────────────────────────────────────────

#     def adaptation_label(self):
#         lvl = self.adaptation_level
#         if lvl >= 4:   return "BRUTAL"
#         if lvl >= 2:   return "HARD"
#         if lvl >= 0:   return "NORMAL"
#         if lvl >= -2:  return "EASY"
#         return "CASUAL"

#     def adaptation_color(self):
#         lvl = self.adaptation_level
#         if lvl >= 4:   return (255,  60,  60)
#         if lvl >= 2:   return (255, 160,  40)
#         if lvl >= 0:   return (255, 255, 100)
#         if lvl >= -2:  return (100, 220, 100)
#         return (120, 180, 255)



# dynamic_ai.py
"""
Dynamic AI Adaptation Engine
Watches player behaviour every N seconds and adjusts enemy parameters in real-time.

Tracked signals:
  - kill_rate       : kills per minute
  - accuracy        : shot accuracy %
  - damage_taken    : damage received per minute
  - movement_speed  : estimated via position trace variance
  - grenade_use     : grenades thrown per minute

Outputs (all stored as mutable dicts so entities.py refs stay valid):
  - ENEMY_VISION_W_REF   : enemy horizontal vision width
  - ENEMY_IDLE_CHANCE_REF: 1/N idle probability denominator
  - enemy_shoot_cd       : enemy shoot cooldown frames (written directly)
  - player speed         : adjusted via player.speed
"""

import math
import time


# ── tuning constants ─────────────────────────────────────────────────────────
EVAL_INTERVAL = 5.0

# pace thresholds for mode inference
RUN_SLOW_PX_S = 35.0
RUN_FAST_PX_S = 95.0
SHOOT_MED_SPM = 30.0
SHOOT_FAST_SPM = 65.0
KILL_MED_KPM = 1.2
KILL_FAST_KPM = 3.0

# enemy profiles per mode
MODE_NORMAL = 0
MODE_HARD = 1
MODE_BRUTAL = 2

MODE_PROFILES = {
    MODE_NORMAL: {
        "name": "NORMAL",
        "vision_w": 150,
        "idle_chance": 200,
        "shoot_cd": 60,
        "level": 0,
        "color": (255, 255, 100),
    },
    MODE_HARD: {
        "name": "HARD",
        "vision_w": 220,
        "idle_chance": 120,
        "shoot_cd": 45,
        "level": 3,
        "color": (255, 160, 40),
    },
    MODE_BRUTAL: {
        "name": "BRUTAL",
        "vision_w": 300,
        "idle_chance": 70,
        "shoot_cd": 33,
        "level": 5,
        "color": (255, 60, 60),
    },
}


class DynamicAI:
    def __init__(self, vision_ref, idle_ref, sim):
        """
        vision_ref  : {"value": int}  – shared dict with entities.py
        idle_ref    : {"value": int}  – shared dict with entities.py
        sim         : SimulationStats instance
        """
        self.vision_ref = vision_ref
        self.idle_ref   = idle_ref
        self.sim        = sim

        # enemy shoot cooldown is pushed to enemies every tick
        self.enemy_shoot_cd = MODE_PROFILES[MODE_NORMAL]["shoot_cd"]

        # player speed multiplier (applied to player.speed)
        self._player_ref     = None
        self._base_speed     = 5
        self.player_speed_mult = 1.0   # 1.0 = normal, range 0.5 – 2.0

        # internal bookmarks for delta calculations
        self._last_eval_time      = time.time()
        self._last_kills          = 0
        self._last_shots          = 0
        self._last_hits           = 0
        self._last_damage_taken   = 0
        self._last_grenades       = 0

        # mode state
        self.mode_index = MODE_NORMAL
        self.performance_score = 0.0
        self._promotion_streak = 0
        self._demotion_streak = 0

        # for display
        self.adaptation_level = MODE_PROFILES[MODE_NORMAL]["level"]
        self.last_event_log   = ["Dynamic mode initialized"]
        self.last_metrics = {
            "run_speed": 0.0,
            "spm": 0.0,
            "kpm": 0.0,
        }

        # player position history for movement estimation
        self._pos_history         = []

        self._apply_mode_profile(self.mode_index)

    def set_player_ref(self, player):
        self._player_ref = player
        self._base_speed = player.speed

    def set_enemy_group(self, enemy_group):
        self._enemy_group = enemy_group

    # ── called every frame ───────────────────────────────────────────────────

    def tick(self, enemy_group):
        """Call once per game frame."""
        now = time.time()

        # record position for movement analysis
        if self._player_ref:
            self._pos_history.append(
                (now, self._player_ref.rect.centerx, self._player_ref.rect.centery)
            )
            # keep only last 10 s
            cutoff = now - 10
            self._pos_history = [(t, x, y) for t, x, y in self._pos_history if t >= cutoff]

        if now - self._last_eval_time >= EVAL_INTERVAL:
            self._evaluate(now, enemy_group)
            self._last_eval_time = now

    # ── internal evaluation ──────────────────────────────────────────────────

    def _evaluate(self, now, enemy_group):
        dt_min = EVAL_INTERVAL / 60.0

        # Delta stats measured only over this window.
        kills_delta = self.sim.kills_player           - self._last_kills
        shots_delta = self.sim.shots_fired_player     - self._last_shots
        hits_delta  = self.sim.hits_player            - self._last_hits
        dmg_delta   = self.sim.damage_taken_by_player - self._last_damage_taken

        # Pace signals used for mode selection.
        kpm  = kills_delta / dt_min
        dpm  = dmg_delta   / dt_min
        spm  = shots_delta / dt_min
        acc  = (hits_delta / shots_delta * 100) if shots_delta > 0 else 0.0
        move_speed = self._estimate_movement()

        self.last_metrics = {
            "run_speed": move_speed,
            "spm": spm,
            "kpm": kpm,
        }

        # Advance bookmarks so next window is fresh
        self._last_kills        = self.sim.kills_player
        self._last_shots        = self.sim.shots_fired_player
        self._last_hits         = self.sim.hits_player
        self._last_damage_taken = self.sim.damage_taken_by_player
        self._last_grenades     = self.sim.grenades_thrown

        events = []

        run_score = self._band_score(move_speed, RUN_SLOW_PX_S, RUN_FAST_PX_S)
        shoot_score = self._band_score(spm, SHOOT_MED_SPM, SHOOT_FAST_SPM)
        kill_score = self._band_score(kpm, KILL_MED_KPM, KILL_FAST_KPM)

        raw_score = (run_score * 0.40) + (shoot_score * 0.25) + (kill_score * 0.35)
        low_activity = move_speed < RUN_SLOW_PX_S and shots_delta == 0 and kills_delta == 0

        # Slow/idle player should pull difficulty back toward NORMAL.
        if low_activity:
            raw_score = max(0.0, raw_score - 0.8)
            events.append("Low activity -> easing to NORMAL")

        # If player is under heavy pressure, avoid pushing up too aggressively.
        if dpm > 120:
            raw_score = max(0.0, raw_score - 0.5)
            events.append("High incoming damage -> pressure reduced")

        # Exponential smoothing keeps transitions stable.
        self.performance_score = (self.performance_score * 0.70) + (raw_score * 0.30)
        if low_activity:
            self.performance_score = max(0.0, self.performance_score - 0.25)

        target_mode = self._target_mode(self.performance_score)

        if target_mode > self.mode_index:
            self._promotion_streak += 1
            self._demotion_streak = 0
        elif target_mode < self.mode_index:
            self._demotion_streak += 1
            self._promotion_streak = 0
        else:
            self._promotion_streak = 0
            self._demotion_streak = 0

        mode_before = self.mode_index
        # Require consistency before moving up, but ease down quickly.
        if self._promotion_streak >= 2 and self.mode_index < MODE_BRUTAL:
            self.mode_index += 1
            self._promotion_streak = 0
        if self._demotion_streak >= 1 and self.mode_index > MODE_NORMAL:
            self.mode_index -= 1
            self._demotion_streak = 0

        self._apply_mode_profile(self.mode_index)

        if self.mode_index != mode_before:
            events.append(f"Mode {MODE_PROFILES[mode_before]['name']} -> {MODE_PROFILES[self.mode_index]['name']}")

        events.append(f"Run {move_speed:.0f}px/s  Shots {spm:.0f}/m  Kills {kpm:.1f}/m")
        events.append(f"Acc {acc:.0f}%  Score {self.performance_score:.2f}")

        # Apply shoot cooldown to live enemies.
        for enemy in enemy_group:
            if enemy.alive:
                enemy._dynamic_shoot_cd = self.enemy_shoot_cd

        # Keep last 3 events for HUD.
        self.last_event_log = events[-3:] if events else ["Monitoring"]

    def _band_score(self, value, mid_threshold, high_threshold):
        if value >= high_threshold:
            return 2.0
        if value >= mid_threshold:
            return 1.0
        return 0.0

    def _target_mode(self, score):
        if score >= 1.45:
            return MODE_BRUTAL
        if score >= 0.85:
            return MODE_HARD
        return MODE_NORMAL

    def _apply_mode_profile(self, mode_index):
        profile = MODE_PROFILES[mode_index]
        self.vision_ref["value"] = profile["vision_w"]
        self.idle_ref["value"] = profile["idle_chance"]
        self.enemy_shoot_cd = profile["shoot_cd"]
        self.adaptation_level = profile["level"]

    def reset_runtime(self):
        self.mode_index = MODE_NORMAL
        self.performance_score = 0.0
        self._promotion_streak = 0
        self._demotion_streak = 0
        self.last_event_log = ["Dynamic mode reset"]
        self.last_metrics = {"run_speed": 0.0, "spm": 0.0, "kpm": 0.0}
        self._pos_history = []
        self._last_eval_time = time.time()
        self._last_kills = self.sim.kills_player
        self._last_shots = self.sim.shots_fired_player
        self._last_hits = self.sim.hits_player
        self._last_damage_taken = self.sim.damage_taken_by_player
        self._last_grenades = self.sim.grenades_thrown
        self._apply_mode_profile(self.mode_index)

    def _estimate_movement(self):
        if len(self._pos_history) < 2:
            return 0
        total_dist = 0
        for i in range(1, len(self._pos_history)):
            t0, x0, y0 = self._pos_history[i - 1]
            t1, x1, y1 = self._pos_history[i]
            total_dist += math.hypot(x1 - x0, y1 - y0)
        elapsed = self._pos_history[-1][0] - self._pos_history[0][0]
        return total_dist / elapsed if elapsed > 0 else 0

    # ── player speed control ─────────────────────────────────────────────────

    def set_player_speed_mult(self, mult):
        """mult: 0.5 – 2.0"""
        self.player_speed_mult = max(0.5, min(2.0, mult))
        if self._player_ref:
            self._player_ref.speed = int(round(self._base_speed * self.player_speed_mult))

    def speed_up(self):
        self.set_player_speed_mult(self.player_speed_mult + 0.25)

    def speed_down(self):
        self.set_player_speed_mult(self.player_speed_mult - 0.25)

    def reset_speed(self):
        self.set_player_speed_mult(1.0)

    # ── HUD helpers ──────────────────────────────────────────────────────────

    def adaptation_label(self):
        return MODE_PROFILES[self.mode_index]["name"]

    def adaptation_color(self):
        return MODE_PROFILES[self.mode_index]["color"]