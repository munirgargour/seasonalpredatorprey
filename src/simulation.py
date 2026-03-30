import sys
import os
import json
import csv
import time
import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from environment import Environment, SEASON_ORDER

SEASON_COLORS = {
    'Spring': '#d4edda',
    'Summer': '#fff3cd',
    'Fall':   '#ffe5cc',
    'Winter': '#cce5ff',
}

class Simulation:
    def __init__(self, config: dict):
        self.config = config
        self.run_id = config.get('run_id', '000')

        seed = config.get('seed', None)
        if seed is not None:
            np.random.seed(seed)

        season_params = config.get('seasons', None)

        self.env = Environment(
            width=config.get('width', 500.0),
            height=config.get('height', 500.0),
            base_grass_spawn_rate=config.get('base_grass_spawn_rate', 5),
            steps_per_season=config.get('steps_per_season', 250),
            season_params=season_params,
        )
        self.env.populate(
            num_rabbits=config.get('num_rabbits', 100),
            num_foxes=config.get('num_foxes', 5),
            initial_grass=config.get('initial_grass', 200),
        )

        self.timestep = 0
        self.timeseries: list[dict] = []

    # ------------------------------------------------------------------
    # Core step
    # ------------------------------------------------------------------
    def step(self):
        prev_season = self.env.current_season_name

        for rabbit in self.env.rabbits:
            rabbit.step(self.env)
        for fox in self.env.foxes:
            fox.step(self.env)

        self.env.step_grass()
        self.env.cleanup_dead_agents()

        self.timestep += 1

        row = {
            'step':          self.timestep,
            'year':          self.env.current_year,
            'season':        self.env.current_season_name,
            'rabbits':       len(self.env.rabbits),
            'foxes':         len(self.env.foxes),
            'grass':         len(self.env.grass_patches),
            'rabbits_born':  self.env.stats_rabbits_born,
            'foxes_born':    self.env.stats_foxes_born,
            'rabbits_eaten': self.env.stats_rabbits_eaten,
            'grass_eaten':   self.env.stats_grass_eaten,
            'metabolism_mult': self.env.metabolism_mult,
            'grass_mult':    self.env.grass_mult,
        }
        self.timeseries.append(row)

        new_season = self.env.current_season_name
        season_marker = f" --> {new_season}" if new_season != prev_season else ""
        print(f"[Run {self.run_id}] Step {self.timestep:>5} | "
              f"Y{self.env.current_year} {self.env.current_season_name:<6} | "
              f"R={len(self.env.rabbits):>4} F={len(self.env.foxes):>3} G={len(self.env.grass_patches):>4}"
              f"{season_marker}")

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def render(self, save_path: str):
        """Spatial snapshot with torus ghost entities at edges."""
        W, H = self.env.bounds
        ghost_margin = 30.0

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_xlim(0, W)
        ax.set_ylim(0, H)
        ax.set_facecolor(SEASON_COLORS.get(self.env.current_season_name, 'white'))
        ax.set_title(
            f"Run {self.run_id} | Step {self.timestep} | "
            f"Y{self.env.current_year} {self.env.current_season_name}",
            fontsize=11
        )

        def ghost_positions(coords):
            """Return original + mirrored ghost copies near edges for torus effect."""
            all_pts = list(coords)
            for pt in coords:
                offsets = []
                if pt[0] < ghost_margin:
                    offsets.append([pt[0] + W, pt[1]])
                if pt[0] > W - ghost_margin:
                    offsets.append([pt[0] - W, pt[1]])
                if pt[1] < ghost_margin:
                    offsets.append([pt[0], pt[1] + H])
                if pt[1] > H - ghost_margin:
                    offsets.append([pt[0], pt[1] - H])
                all_pts.extend(offsets)
            return np.array(all_pts) if all_pts else np.empty((0, 2))

        # Grass
        if len(self.env.grass_patches) > 0:
            g = ghost_positions(self.env.grass_patches)
            ax.scatter(g[:, 0], g[:, 1], c='green', alpha=0.4, s=8, label='Grass')

        # Rabbits
        rabbit_coords = np.array([r.position for r in self.env.rabbits if r.is_alive])
        if len(rabbit_coords) > 0:
            rg = ghost_positions(rabbit_coords)
            ax.scatter(rg[:, 0], rg[:, 1], c='royalblue', s=18, alpha=0.8, label='Rabbits')

        # Foxes
        fox_coords = np.array([f.position for f in self.env.foxes if f.is_alive])
        if len(fox_coords) > 0:
            fg = ghost_positions(fox_coords)
            ax.scatter(fg[:, 0], fg[:, 1], c='red', marker='x', s=45, linewidths=1.5, label='Foxes')

        ax.legend(loc='upper right', fontsize=9)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')

        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, dpi=90, bbox_inches='tight')
        plt.close(fig)

    def render_population_chart(self, save_path: str):
        """Long-phase population chart with season background bands."""
        steps  = [r['step']    for r in self.timeseries]
        rabbits = [r['rabbits'] for r in self.timeseries]
        foxes   = [r['foxes']   for r in self.timeseries]
        grass   = [r['grass']   for r in self.timeseries]

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
        fig.suptitle(f"Run {self.run_id} — Population Dynamics Over Time", fontsize=13)

        sps = self.env.steps_per_season
        total_steps = self.timestep
        total_seasons = (total_steps // sps) + 1

        for ax in (ax1, ax2):
            for s in range(total_seasons):
                sname = SEASON_ORDER[s % 4]
                x0 = s * sps
                x1 = min((s + 1) * sps, total_steps)
                ax.axvspan(x0, x1, alpha=0.25, color=SEASON_COLORS[sname], zorder=0)
                if s % 4 == 0 and s > 0:
                    ax.axvline(x=x0, color='grey', linestyle='--', linewidth=0.8, alpha=0.6)

        ax1.plot(steps, rabbits, color='royalblue', linewidth=1.2, label='Rabbits')
        ax1.plot(steps, foxes,   color='red',       linewidth=1.2, label='Foxes')
        ax1.set_ylabel('Population Count')
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)

        ax2.plot(steps, grass, color='green', linewidth=1.0, label='Grass Patches')
        ax2.set_ylabel('Grass Patches')
        ax2.set_xlabel('Simulation Step')
        ax2.legend(loc='upper right')
        ax2.grid(True, alpha=0.3)

        season_patches = [mpatches.Patch(color=SEASON_COLORS[s], label=s, alpha=0.6)
                          for s in SEASON_ORDER]
        fig.legend(handles=season_patches, loc='lower center', ncol=4,
                   fontsize=9, title='Season', bbox_to_anchor=(0.5, -0.01))

        fig.tight_layout(rect=[0, 0.04, 1, 1])
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, dpi=110, bbox_inches='tight')
        plt.close(fig)

    # ------------------------------------------------------------------
    # Data export
    # ------------------------------------------------------------------
    def export_timeseries(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not self.timeseries:
            return
        keys = list(self.timeseries[0].keys())
        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.timeseries)

    def export_summary(self, path: str, wall_time: float):
        rabbits_vals = [r['rabbits'] for r in self.timeseries]
        foxes_vals   = [r['foxes']   for r in self.timeseries]
        grass_vals   = [r['grass']   for r in self.timeseries]

        last = self.timeseries[-1] if self.timeseries else {}

        summary = {
            'run_id':             self.run_id,
            'total_steps':        self.timestep,
            'wall_time_seconds':  round(wall_time, 2),
            'final_rabbits':      last.get('rabbits', 0),
            'final_foxes':        last.get('foxes', 0),
            'final_grass':        last.get('grass', 0),
            'max_rabbits':        int(max(rabbits_vals)) if rabbits_vals else 0,
            'min_rabbits':        int(min(rabbits_vals)) if rabbits_vals else 0,
            'avg_rabbits':        round(float(np.mean(rabbits_vals)), 2) if rabbits_vals else 0,
            'max_foxes':          int(max(foxes_vals)) if foxes_vals else 0,
            'min_foxes':          int(min(foxes_vals)) if foxes_vals else 0,
            'avg_foxes':          round(float(np.mean(foxes_vals)), 2) if foxes_vals else 0,
            'avg_grass':          round(float(np.mean(grass_vals)), 2) if grass_vals else 0,
            'total_rabbits_born': last.get('rabbits_born', 0),
            'total_foxes_born':   last.get('foxes_born', 0),
            'total_rabbits_eaten':last.get('rabbits_eaten', 0),
            'total_grass_eaten':  last.get('grass_eaten', 0),
            'extinction_rabbits': last.get('rabbits', 1) == 0,
            'extinction_foxes':   last.get('foxes', 1) == 0,
        }
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(summary, f, indent=2)
        return summary

    def export_config(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(self.config, f, indent=2)

    # ------------------------------------------------------------------
    # Full run
    # ------------------------------------------------------------------
    def run(self, output_dir: str, snapshot_interval: int = None):
        steps = self.config.get('steps', 1000)
        if snapshot_interval is None:
            snapshot_interval = max(1, steps // 5)

        os.makedirs(output_dir, exist_ok=True)
        self.export_config(os.path.join(output_dir, f'run_{self.run_id}_config.json'))

        # Frame 0
        self.render(os.path.join(output_dir, f'run_{self.run_id}_frame_0000.png'))

        t_start = time.time()
        for _ in range(steps):
            self.step()
            if self.timestep % snapshot_interval == 0 or self.timestep == steps:
                self.render(os.path.join(output_dir,
                    f'run_{self.run_id}_frame_{self.timestep:04d}.png'))

            # Early termination if both populations extinct
            if not self.env.rabbits and not self.env.foxes:
                print(f"[Run {self.run_id}] All animals extinct at step {self.timestep}.")
                break

        wall_time = time.time() - t_start

        self.export_timeseries(os.path.join(output_dir, f'run_{self.run_id}_timeseries.csv'))
        summary = self.export_summary(os.path.join(output_dir, f'run_{self.run_id}_summary.json'),
                                      wall_time)
        self.render_population_chart(os.path.join(output_dir, f'run_{self.run_id}_population.png'))

        print(f"[Run {self.run_id}] Done in {wall_time:.1f}s | "
              f"Final R={summary['final_rabbits']} F={summary['final_foxes']}")
        return summary


# ----------------------------------------------------------------------
# CLI entry point (single run)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seasonal Predator-Prey Simulation (M3)")
    parser.add_argument('--config', type=str, default=None,
                        help='Path to JSON config file')
    parser.add_argument('--run_id',      default='001')
    parser.add_argument('--steps',       type=int,   default=1000)
    parser.add_argument('--num_rabbits', type=int,   default=100)
    parser.add_argument('--num_foxes',   type=int,   default=5)
    parser.add_argument('--initial_grass', type=int, default=200)
    parser.add_argument('--seed',        type=int,   default=42)
    parser.add_argument('--output_dir',  default='../output')
    args = parser.parse_args()

    if args.config:
        with open(args.config) as f:
            config = json.load(f)
    else:
        config = {
            'run_id':       args.run_id,
            'steps':        args.steps,
            'num_rabbits':  args.num_rabbits,
            'num_foxes':    args.num_foxes,
            'initial_grass':args.initial_grass,
            'seed':         args.seed,
        }

    sim = Simulation(config)
    sim.run(output_dir=args.output_dir)
