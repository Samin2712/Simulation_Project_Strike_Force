import os
import csv
import time


def _clear_session_path_runs(folder="simulation_results"):
    """
    Called ONCE at program startup.
    Deletes all path_run_*.csv files so this execution starts fresh at run 1.
    runs.csv is kept (appended across executions).
    """
    if not os.path.isdir(folder):
        return
    for fname in os.listdir(folder):
        if fname.startswith("path_run_") and fname.endswith(".csv"):
            try:
                os.remove(os.path.join(folder, fname))
            except OSError:
                pass


# Run this cleanup the moment the module is first imported (once per process).
_clear_session_path_runs()


class SimulationStats:
    def __init__(self):
        # run_id tracks restarts within this execution session (resets to 0 each launch).
        self.run_id = 0
        self.reset(level_started=1)
        self._saved_this_end = False

    def reset(self, level_started: int):
        self.run_id += 1          # 1, 2, 3 … within this session
        self.level_started = level_started
        self.started_at = time.time()
        self.ended_at = None

        # player stats
        self.shots_fired_player    = 0
        self.hits_player           = 0
        self.kills_player          = 0
        self.damage_done_by_player = 0

        self.grenades_thrown = 0
        self.grenade_kills   = 0
        self.grenade_damage  = 0

        # enemy → player
        self.damage_taken_by_player = 0
        self._saved_this_end = False

    # ── hooks ──────────────────────────────────────────────────────────

    def tick_trace(self):
        pass  # called every frame; extend if you want live tracking

    def survival_time(self) -> float:
        end_t = self.ended_at if self.ended_at is not None else time.time()
        return max(0.0, end_t - self.started_at)

    def accuracy_player(self) -> float:
        if self.shots_fired_player <= 0:
            return 0.0
        return (self.hits_player / self.shots_fired_player) * 100.0

    # ── recorders ──────────────────────────────────────────────────────

    def record_shot(self, owner: str):
        if owner == 'player':
            self.shots_fired_player += 1

    def record_hit(self, attacker: str, victim: str, damage: int):
        if attacker == 'player' and victim == 'enemy':
            self.hits_player += 1
            self.damage_done_by_player += damage
        if attacker == 'enemy' and victim == 'player':
            self.damage_taken_by_player += damage

    def record_kill(self, killer: str, method: str = 'bullet'):
        if killer == 'player':
            self.kills_player += 1
            if method == 'grenade':
                self.grenade_kills += 1

    def record_grenade_throw(self):
        self.grenades_thrown += 1

    def record_grenade_damage(self, damage: int):
        self.grenade_damage += damage
        self.damage_done_by_player += damage

    # ── save ───────────────────────────────────────────────────────────

    def save_outputs_once(self, final_level: int, completed: bool):
        if self._saved_this_end:
            return
        self._saved_this_end = True

        os.makedirs("simulation_results", exist_ok=True)

        # ── runs.csv  (append across ALL executions) ──────────────────
        runs_path  = os.path.join("simulation_results", "runs.csv")
        file_exists = os.path.exists(runs_path)

        with open(runs_path, "a", newline="") as f:
            w = csv.writer(f)
            if not file_exists:
                w.writerow([
                    "run_id", "level_started", "final_level", "completed",
                    "survival_time",
                    "kills", "shots_fired", "hits", "accuracy",
                    "damage_done", "damage_taken",
                    "grenades_thrown", "grenade_kills", "grenade_damage"
                ])
            w.writerow([
                self.run_id, self.level_started, final_level, int(completed),
                f"{self.survival_time():.2f}",
                self.kills_player, self.shots_fired_player, self.hits_player,
                f"{self.accuracy_player():.1f}",
                self.damage_done_by_player, self.damage_taken_by_player,
                self.grenades_thrown, self.grenade_kills, self.grenade_damage
            ])

        # ── path_run_<id>.csv  (fresh each execution, overwrite if exists) ──
        # run_id resets to 1 on each new program launch (old files were wiped on import).
        # Restarting mid-session: run_id increments → path_run_1, path_run_2, …
        # Next launch: files wiped again → path_run_1, path_run_2, …
        path_csv = os.path.join("simulation_results", f"path_run_{self.run_id}.csv")
        with open(path_csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["t", "x", "y"])
            # (extend here if you record player positions via tick_trace)


simulation_stats.py

import os
import csv
import time


def _clear_session_path_runs(folder="simulation_results"):
    """
    Called ONCE when the module is first imported (i.e. once per program launch).
    Deletes all  path_run_*.csv  files so this execution starts fresh at run_id = 1.
    runs.csv is intentionally kept — it accumulates across all executions.
    """
    if not os.path.isdir(folder):
        return
    for fname in os.listdir(folder):
        if fname.startswith("path_run_") and fname.endswith(".csv"):
            try:
                os.remove(os.path.join(folder, fname))
            except OSError:
                pass


# Wipe old path_run files the moment this module is imported (once per process).
_clear_session_path_runs()


class SimulationStats:
    def __init__(self):
        # run_id starts at 0; first call to reset() will bring it to 1.
        # __init__ does NOT call reset() — that is done explicitly from main when
        # the player actually starts a game, so run_id 1 == first real run.
        self.run_id = 0

        # initialise all stat fields to safe defaults (no run_id increment here)
        self._init_fields(level_started=1)

        # in-memory position trace: list of (t, x, y) tuples recorded each frame
        self._path_trace = []

        # reference to the player sprite — set via set_player_ref() from main
        self._player = None

    # ── internal helpers ────────────────────────────────────────────────

    def _init_fields(self, level_started: int):
        """Zero out all stats WITHOUT touching run_id."""
        self.level_started = level_started
        self.started_at    = time.time()
        self.ended_at      = None

        self.shots_fired_player     = 0
        self.hits_player            = 0
        self.kills_player           = 0
        self.damage_done_by_player  = 0

        self.grenades_thrown = 0
        self.grenade_kills   = 0
        self.grenade_damage  = 0

        self.damage_taken_by_player = 0
        self._saved_this_end        = False

    # ── public API ──────────────────────────────────────────────────────

    def set_player_ref(self, player):
        """Call this from main whenever a new player object is created."""
        self._player = player

    def reset(self, level_started: int):
        """
        Called once per game run (not at construction).
        Increments run_id:  1st play → 1,  1st restart → 2,  etc.
        Path trace is cleared ready for the new run.
        """
        self.run_id += 1
        self._path_trace = []
        self._init_fields(level_started)

    def tick_trace(self):
        """
        Called every frame while the game is running.
        Records the player's current pixel position and elapsed time.
        """
        if self._player is None:
            return
        t = self.survival_time()
        x = self._player.rect.centerx
        y = self._player.rect.centery
        self._path_trace.append((round(t, 3), x, y))

    # ── stat recorders ──────────────────────────────────────────────────

    def survival_time(self) -> float:
        end_t = self.ended_at if self.ended_at is not None else time.time()
        return max(0.0, end_t - self.started_at)

    def accuracy_player(self) -> float:
        if self.shots_fired_player <= 0:
            return 0.0
        return (self.hits_player / self.shots_fired_player) * 100.0

    def record_shot(self, owner: str):
        if owner == 'player':
            self.shots_fired_player += 1

    def record_hit(self, attacker: str, victim: str, damage: int):
        if attacker == 'player' and victim == 'enemy':
            self.hits_player += 1
            self.damage_done_by_player += damage
        if attacker == 'enemy' and victim == 'player':
            self.damage_taken_by_player += damage

    def record_kill(self, killer: str, method: str = 'bullet'):
        if killer == 'player':
            self.kills_player += 1
            if method == 'grenade':
                self.grenade_kills += 1

    def record_grenade_throw(self):
        self.grenades_thrown += 1

    def record_grenade_damage(self, damage: int):
        self.grenade_damage += damage
        self.damage_done_by_player += damage

    # ── save ────────────────────────────────────────────────────────────

    def save_outputs_once(self, final_level: int, completed: bool):
        """
        Saves two files (called once when a run ends):

          simulation_results/runs.csv
              → one row per run, appended forever across all executions.

          simulation_results/path_run_<run_id>.csv
              → full player path for this run (t, x, y per frame).
              → numbering resets to 1 each program launch because
                _clear_session_path_runs() wiped old files on import.
        """
        if self._saved_this_end:
            return
        self._saved_this_end = True

        os.makedirs("simulation_results", exist_ok=True)

        # ── runs.csv ──────────────────────────────────────────────────
        runs_path   = os.path.join("simulation_results", "runs.csv")
        file_exists = os.path.exists(runs_path)

        with open(runs_path, "a", newline="") as f:
            w = csv.writer(f)
            if not file_exists:
                w.writerow([
                    "run_id", "level_started", "final_level", "completed",
                    "survival_time",
                    "kills", "shots_fired", "hits", "accuracy",
                    "damage_done", "damage_taken",
                    "grenades_thrown", "grenade_kills", "grenade_damage"
                ])
            w.writerow([
                self.run_id,
                self.level_started,
                final_level,
                int(completed),
                f"{self.survival_time():.2f}",
                self.kills_player,
                self.shots_fired_player,
                self.hits_player,
                f"{self.accuracy_player():.1f}",
                self.damage_done_by_player,
                self.damage_taken_by_player,
                self.grenades_thrown,
                self.grenade_kills,
                self.grenade_damage,
            ])

        # ── path_run_<id>.csv  (always overwrite — fresh each run) ────
        path_csv = os.path.join("simulation_results", f"path_run_{self.run_id}.csv")
        with open(path_csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["t", "x", "y"])
            for row in self._path_trace:
                w.writerow(row)