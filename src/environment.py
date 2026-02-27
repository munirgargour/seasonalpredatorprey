import numpy as np
from scipy.spatial import KDTree

class Environment:
    def __init__(self, width=500.0, height=500.0):
        self.bounds = (width, height)
        # We will store grass as a numpy array of coordinates (x, y)
        self.grass_patches = np.empty((0, 2), dtype=float)
        self.base_spawn_rate = 5
        self.base_spawn_rate = 5
        self.rabbits = []
        self.foxes = []
        
        # Debug / Stat Tracking
        self.stats_grass_eaten = 0
        self.stats_rabbits_eaten = 0
        self.stats_rabbits_born = 0
        self.stats_foxes_born = 0

    def populate(self, num_rabbits, num_foxes, initial_grass):
        from entities import Rabbit, Fox
        
        # Initial Grass
        for _ in range(initial_grass):
            self.spawn_grass_patch()

        # Initial Rabbits
        for _ in range(num_rabbits):
            x = np.random.uniform(0, self.bounds[0])
            y = np.random.uniform(0, self.bounds[1])
            self.rabbits.append(Rabbit(x, y))

        # Initial Foxes
        for _ in range(num_foxes):
            x = np.random.uniform(0, self.bounds[0])
            y = np.random.uniform(0, self.bounds[1])
            self.foxes.append(Fox(x, y))

    def spawn_grass_patch(self):
        x = np.random.uniform(0, self.bounds[0])
        y = np.random.uniform(0, self.bounds[1])
        self.grass_patches = np.vstack((self.grass_patches, [x, y]))

    def step_grass(self):
        """Regenerate grass: new_grass_per_timestep = 5"""
        for _ in range(self.base_spawn_rate):
            self.spawn_grass_patch()

    def get_nearest_grass(self, position, radius):
        """Use KDTree to find the nearest grass patch."""
        if len(self.grass_patches) == 0:
            return None
            
        tree = KDTree(self.grass_patches)
        # Using scipy.spatial.KDTree.query_ball_point behavior through KDTree.query
        dist, index = tree.query(position, distance_upper_bound=radius)
        
        if dist != float('inf') and index < len(self.grass_patches):
            return self.grass_patches[index]
        return None

    def remove_grass(self, position):
        """Remove a piece of grass at the exact position."""
        # Find index of this exact grass patch
        distances = np.linalg.norm(self.grass_patches - position, axis=1)
        if len(distances) > 0:
            min_idx = np.argmin(distances)
            if distances[min_idx] < 0.1: # Threshold for floating point equality
                self.grass_patches = np.delete(self.grass_patches, min_idx, axis=0)

    def get_rabbits_in_radius(self, position, radius) -> list:
        """Return all alive rabbits within distance."""
        alive_rabbits = [r for r in self.rabbits if r.is_alive]
        if not alive_rabbits:
            return []
            
        rabbit_positions = np.array([r.position for r in alive_rabbits])
        tree = KDTree(rabbit_positions)
        
        indices = tree.query_ball_point(position, r=radius)
        return [alive_rabbits[i] for i in indices]

    def get_foxes_in_radius(self, position, radius) -> list:
        """Return all alive foxes within distance."""
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
