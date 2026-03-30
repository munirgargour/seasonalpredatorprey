import numpy as np
from scipy.spatial import KDTree

SEASON_ORDER = ['Spring', 'Summer', 'Fall', 'Winter']

DEFAULT_SEASON_PARAMS = {
    'Spring': {'metabolism_mult': 0.8,  'grass_mult': 2.0},
    'Summer': {'metabolism_mult': 1.0,  'grass_mult': 1.5},
    'Fall':   {'metabolism_mult': 1.1,  'grass_mult': 0.7},
    'Winter': {'metabolism_mult': 1.2,  'grass_mult': 0.5},
}

class Environment:
    def __init__(self, width=500.0, height=500.0, base_grass_spawn_rate=5,
                 steps_per_season=250, season_params=None):
        self.bounds = (width, height)
        self.grass_patches = np.empty((0, 2), dtype=float)
        self.base_spawn_rate = base_grass_spawn_rate
        self.steps_per_season = steps_per_season
        self.season_params = season_params if season_params else DEFAULT_SEASON_PARAMS

        self.rabbits = []
        self.foxes = []

        # Season state
        self._step_count = 0  # total steps elapsed

        # Stats
        self.stats_grass_eaten = 0
        self.stats_rabbits_eaten = 0
        self.stats_rabbits_born = 0
        self.stats_foxes_born = 0

    # ------------------------------------------------------------------
    # Season helpers
    # ------------------------------------------------------------------
    @property
    def current_season_index(self):
        return (self._step_count // self.steps_per_season) % 4

    @property
    def current_season_name(self):
        return SEASON_ORDER[self.current_season_index]

    @property
    def current_year(self):
        return (self._step_count // (self.steps_per_season * 4)) + 1

    @property
    def metabolism_mult(self):
        return self.season_params[self.current_season_name]['metabolism_mult']

    @property
    def grass_mult(self):
        return self.season_params[self.current_season_name]['grass_mult']

    # ------------------------------------------------------------------
    # Population
    # ------------------------------------------------------------------
    def populate(self, num_rabbits, num_foxes, initial_grass):
        from entities import Rabbit, Fox

        for _ in range(initial_grass):
            self.spawn_grass_patch()

        for _ in range(num_rabbits):
            x = np.random.uniform(0, self.bounds[0])
            y = np.random.uniform(0, self.bounds[1])
            self.rabbits.append(Rabbit(x, y))

        for _ in range(num_foxes):
            x = np.random.uniform(0, self.bounds[0])
            y = np.random.uniform(0, self.bounds[1])
            self.foxes.append(Fox(x, y))

    # ------------------------------------------------------------------
    # Grass
    # ------------------------------------------------------------------
    def spawn_grass_patch(self):
        x = np.random.uniform(0, self.bounds[0])
        y = np.random.uniform(0, self.bounds[1])
        self.grass_patches = np.vstack((self.grass_patches, [x, y]))

    def step_grass(self):
        """Regenerate grass scaled by current season grass multiplier."""
        num_new = max(0, round(self.base_spawn_rate * self.grass_mult))
        for _ in range(num_new):
            self.spawn_grass_patch()
        self._step_count += 1

    def get_nearest_grass(self, position, radius):
        if len(self.grass_patches) == 0:
            return None
        tree = KDTree(self.grass_patches)
        dist, index = tree.query(position, distance_upper_bound=radius)
        if dist != float('inf') and index < len(self.grass_patches):
            return self.grass_patches[index]
        return None

    def remove_grass(self, position):
        distances = np.linalg.norm(self.grass_patches - position, axis=1)
        if len(distances) > 0:
            min_idx = np.argmin(distances)
            if distances[min_idx] < 0.1:
                self.grass_patches = np.delete(self.grass_patches, min_idx, axis=0)

    # ------------------------------------------------------------------
    # Spatial queries
    # ------------------------------------------------------------------
    def get_rabbits_in_radius(self, position, radius) -> list:
        alive_rabbits = [r for r in self.rabbits if r.is_alive]
        if not alive_rabbits:
            return []
        rabbit_positions = np.array([r.position for r in alive_rabbits])
        tree = KDTree(rabbit_positions)
        indices = tree.query_ball_point(position, r=radius)
        return [alive_rabbits[i] for i in indices]

    def get_foxes_in_radius(self, position, radius) -> list:
        alive_foxes = [f for f in self.foxes if f.is_alive]
        if not alive_foxes:
            return []
        fox_positions = np.array([f.position for f in alive_foxes])
        tree = KDTree(fox_positions)
        indices = tree.query_ball_point(position, r=radius)
        return [alive_foxes[i] for i in indices]

    def cleanup_dead_agents(self):
        self.rabbits = [r for r in self.rabbits if r.is_alive]
        self.foxes = [f for f in self.foxes if f.is_alive]
