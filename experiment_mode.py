import csv
import json
import math
import os
import random
import time


class ExperimentManager:
    """
    Handles Experiment Mode parameter distributions, sampling, application,
    and post-run reporting.
    """

    PARAM_CONFIG = {
        "enemy_vision_w": {
            "label": "Enemy Vision Width",
            "kind": "int",
            "min": 90,
            "max": 340,
            "default": 150,
            "best": "normal",
            "options": ["normal", "uniform", "poisson", "binomial", "exponential"],
        },
        "enemy_idle_chance": {
            "label": "Enemy Idle Chance (1/N)",
            "kind": "int",
            "min": 60,
            "max": 420,
            "default": 200,
            "best": "binomial",
            "options": ["binomial", "poisson", "normal", "uniform", "exponential"],
        },
        "enemy_shoot_cd": {
            "label": "Enemy Shoot Cooldown (frames)",
            "kind": "int",
            "min": 28,
            "max": 90,
            "default": 60,
            "best": "poisson",
            "options": ["poisson", "normal", "uniform", "binomial", "exponential"],
        },
        "enemy_speed_mult": {
            "label": "Enemy Speed Multiplier",
            "kind": "float",
            "min": 0.70,
            "max": 1.60,
            "default": 1.00,
            "best": "normal",
            "options": ["normal", "uniform", "binomial", "poisson", "exponential"],
        },
        "enemy_health_mult": {
            "label": "Enemy Health Multiplier",
            "kind": "float",
            "min": 0.70,
            "max": 1.90,
            "default": 1.00,
            "best": "normal",
            "options": ["normal", "uniform", "binomial", "poisson", "exponential"],
        },
    }

    def __init__(self, output_dir="experiment_results"):
        self.output_dir = output_dir
        self.runtime_defaults = {}

    def set_runtime_defaults(self, defaults):
        self.runtime_defaults = {k: float(v) for k, v in defaults.items() if v is not None}

    def get_effective_default(self, param_name):
        cfg = self.PARAM_CONFIG[param_name]
        return self.runtime_defaults.get(param_name, cfg["default"])

    def default_distribution_selection(self):
        return {k: v["best"] for k, v in self.PARAM_CONFIG.items()}

    def parameter_order(self):
        return list(self.PARAM_CONFIG.keys())

    def sample_values(self, distribution_selection):
        sampled = {}
        for param, cfg in self.PARAM_CONFIG.items():
            dist = distribution_selection.get(param, cfg["best"])
            value = self._sample_one(cfg, dist, param_name=param)
            sampled[param] = value
        return sampled

    def preview_samples(self, param_name, distribution_name, sample_count=240):
        cfg = self.PARAM_CONFIG[param_name]
        return [self._sample_one(cfg, distribution_name, param_name=param_name) for _ in range(sample_count)]

    def distribution_explanation(self, distribution_name):
        explanations = {
            "uniform": "All values in the range have equal chance.",
            "normal": "Most samples cluster near the default, with rare extremes.",
            "exponential": "Many small/near-default values, fewer large ones; strongly skewed.",
            "poisson": "Discrete event-style distribution around a mean count.",
            "binomial": "Results come from repeated yes/no trials, centered around a success rate.",
        }
        return explanations.get(distribution_name, "Distribution preview.")

    def distribution_label_color(self, distribution_name):
        colors = {
            "uniform": (80, 170, 255),
            "normal": (255, 195, 80),
            "exponential": (255, 125, 65),
            "poisson": (170, 125, 255),
            "binomial": (80, 220, 150),
        }
        return colors.get(distribution_name, (220, 220, 220))

    def apply_to_refs(self, sampled_values, enemy_vision_w_ref, enemy_idle_chance_ref):
        enemy_vision_w_ref["value"] = int(sampled_values["enemy_vision_w"])
        enemy_idle_chance_ref["value"] = int(sampled_values["enemy_idle_chance"])

    def apply_to_enemy_group(self, enemy_group, sampled_values):
        shoot_cd = int(sampled_values["enemy_shoot_cd"])
        speed_mult = float(sampled_values["enemy_speed_mult"])
        hp_mult = float(sampled_values["enemy_health_mult"])

        for enemy in enemy_group:
            if not hasattr(enemy, "_exp_base_speed"):
                enemy._exp_base_speed = enemy.speed
                enemy._exp_base_max_health = enemy.max_health
                enemy._exp_base_health = enemy.health

            enemy._dynamic_shoot_cd = shoot_cd

            tuned_speed = max(1, int(round(enemy._exp_base_speed * speed_mult)))
            enemy.speed = tuned_speed

            if not hasattr(enemy, "_exp_tuned_health"):
                tuned_max = max(1, int(round(enemy._exp_base_max_health * hp_mult)))
                enemy.max_health = tuned_max
                enemy.health = max(1, int(round(enemy._exp_base_health * hp_mult)))
                enemy._exp_tuned_health = True

    def save_experiment_report(self, sim, final_level, completed, distribution_selection, sampled_values):
        os.makedirs(self.output_dir, exist_ok=True)

        run_id = self._next_run_id()
        ts = int(time.time())

        survival = sim.survival_time()
        accuracy = sim.accuracy_player()
        kpm = sim.kills_player / (survival / 60.0 + 1e-6)
        dpm_taken = sim.damage_taken_by_player / (survival / 60.0 + 1e-6)

        row = {
            "run_id": run_id,
            "timestamp": ts,
            "completed": int(completed),
            "level_started": sim.level_started,
            "final_level": final_level,
            "survival_time": round(survival, 2),
            "kills": sim.kills_player,
            "shots_fired": sim.shots_fired_player,
            "hits": sim.hits_player,
            "accuracy": round(accuracy, 1),
            "kpm": round(kpm, 2),
            "damage_done": sim.damage_done_by_player,
            "damage_taken": sim.damage_taken_by_player,
            "damage_taken_per_min": round(dpm_taken, 2),
            "grenades_thrown": sim.grenades_thrown,
            "grenade_kills": sim.grenade_kills,
            "grenade_damage": sim.grenade_damage,
            "dist_enemy_vision_w": distribution_selection["enemy_vision_w"],
            "dist_enemy_idle_chance": distribution_selection["enemy_idle_chance"],
            "dist_enemy_shoot_cd": distribution_selection["enemy_shoot_cd"],
            "dist_enemy_speed_mult": distribution_selection["enemy_speed_mult"],
            "dist_enemy_health_mult": distribution_selection["enemy_health_mult"],
            "val_enemy_vision_w": sampled_values["enemy_vision_w"],
            "val_enemy_idle_chance": sampled_values["enemy_idle_chance"],
            "val_enemy_shoot_cd": sampled_values["enemy_shoot_cd"],
            "val_enemy_speed_mult": sampled_values["enemy_speed_mult"],
            "val_enemy_health_mult": sampled_values["enemy_health_mult"],
        }

        self._append_csv_row(row)

        json_path = os.path.join(self.output_dir, f"run_{run_id}_{ts}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(row, f, indent=2)

        return json_path

    def _next_run_id(self):
        runs_csv = os.path.join(self.output_dir, "runs.csv")
        if not os.path.exists(runs_csv):
            return 1

        last_run_id = 0
        with open(runs_csv, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    last_run_id = max(last_run_id, int(row.get("run_id", 0)))
                except (TypeError, ValueError):
                    pass
        return last_run_id + 1

    def _append_csv_row(self, row):
        runs_csv = os.path.join(self.output_dir, "runs.csv")
        file_exists = os.path.exists(runs_csv)

        fieldnames = [
            "run_id", "timestamp", "completed", "level_started", "final_level",
            "survival_time", "kills", "shots_fired", "hits", "accuracy", "kpm",
            "damage_done", "damage_taken", "damage_taken_per_min",
            "grenades_thrown", "grenade_kills", "grenade_damage",
            "dist_enemy_vision_w", "dist_enemy_idle_chance", "dist_enemy_shoot_cd",
            "dist_enemy_speed_mult", "dist_enemy_health_mult",
            "val_enemy_vision_w", "val_enemy_idle_chance", "val_enemy_shoot_cd",
            "val_enemy_speed_mult", "val_enemy_health_mult",
        ]

        with open(runs_csv, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)

    def _sample_one(self, cfg, dist, param_name=None):
        lo = cfg["min"]
        hi = cfg["max"]
        center = self.get_effective_default(param_name) if param_name is not None else cfg["default"]

        if dist == "uniform":
            value = random.uniform(lo, hi)
        elif dist == "normal":
            sigma = (hi - lo) / 6.0
            value = random.gauss(center, sigma)
        elif dist == "exponential":
            value = self._sample_exponential(lo, hi, center)
        elif dist == "poisson":
            value = self._sample_poisson(lo, hi, center)
        elif dist == "binomial":
            value = self._sample_binomial(lo, hi, center)
        else:
            value = center

        value = max(lo, min(hi, value))

        if cfg["kind"] == "int":
            return int(round(value))

        return round(float(value), 2)

    def _sample_exponential(self, lo, hi, center):
        span = hi - lo
        mid = lo + (span * 0.5)

        if center <= mid:
            scale = max(1e-6, center - lo)
            value = lo + random.expovariate(1.0 / max(scale, span * 0.15))
        else:
            scale = max(1e-6, hi - center)
            value = hi - random.expovariate(1.0 / max(scale, span * 0.15))

        return max(lo, min(hi, value))

    def _sample_poisson(self, lo, hi, center):
        lam = max(0.05, center - lo)
        k = self._poisson_knuth_or_normal(lam)
        value = lo + k
        return max(lo, min(hi, value))

    def _sample_binomial(self, lo, hi, center):
        n = max(1, int(round(hi - lo)))
        p = (center - lo) / max(1e-9, (hi - lo))
        p = max(0.01, min(0.99, p))

        if n <= 220:
            successes = 0
            for _ in range(n):
                if random.random() < p:
                    successes += 1
        else:
            mean = n * p
            std = math.sqrt(n * p * (1.0 - p))
            successes = int(round(random.gauss(mean, std)))
            successes = max(0, min(n, successes))

        value = lo + (successes / n) * (hi - lo)
        return max(lo, min(hi, value))

    def _poisson_knuth_or_normal(self, lam):
        if lam < 30.0:
            l = math.exp(-lam)
            k = 0
            p = 1.0
            while p > l:
                k += 1
                p *= random.random()
            return max(0, k - 1)

        approx = int(round(random.gauss(lam, math.sqrt(lam))))
        return max(0, approx)
