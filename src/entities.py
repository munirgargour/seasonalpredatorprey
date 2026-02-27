import numpy as np

class Animal:
    def __init__(self, x, y, max_energy, initial_energy, speed, base_metabolism):
        self.position = np.array([x, y], dtype=float)
        self.max_energy = max_energy
        self.energy = initial_energy
        self.speed = speed
        self.base_metabolism = base_metabolism
        self.is_alive = True

    def move(self, vector, bounds):
        """Move un-normalized vector distance, wrap around bounds (toroidal)."""
        self.position += vector
        self.position[0] = self.position[0] % bounds[0]
        self.position[1] = self.position[1] % bounds[1]

    def metabolize(self):
        self.energy -= self.base_metabolism
        if self.energy <= 0:
            self.is_alive = False

class Rabbit(Animal):
    def __init__(self, x, y):
        # Max Energy = 100, Initial Energy = 49, Movement Speed = 10.0, Base Metabolism = 0.25
        super().__init__(x, y, max_energy=100.0, initial_energy=49.0, speed=10.0, base_metabolism=0.25)
        self.foraging_radius = 25.0  # Increased 5x from 5.0
        self.energy_per_grass = 10.0

    def assess_hunger(self) -> float:
        """Returns 1 - E/Emax"""
        return 1.0 - (self.energy / self.max_energy)

    def step(self, env):
        if not self.is_alive:
            return

        # 1. Check Reproduction Mode First
        if self.energy > 50.0:
            # Look for a mate
            nearby_rabbits = env.get_rabbits_in_radius(self.position, radius=100.0) # Increased 5x from 20.0
            potential_mates = [r for r in nearby_rabbits if r is not self and r.energy > 50.0]
            
            if potential_mates:
                # Find nearest mate
                nearest_mate = min(potential_mates, key=lambda r: np.linalg.norm(r.position - self.position))
                direction = nearest_mate.position - self.position
                dist = np.linalg.norm(direction)
                
                if dist < 10.0:
                    # Close enough to reproduce, handled in reproduce()
                    move_vector = np.array([0.0, 0.0])
                else:
                    move_vector = (direction / dist) * self.speed
                
                self.move(move_vector, env.bounds)
                self.metabolize()
                self.reproduce(env, potential_mates)
                return

        # 2. Algorithm 1: Hunger-Driven Foraging
        hunger = self.assess_hunger()
        
        if hunger > 0.10: # Energy < 90%
            # Find nearest grass within radius
            nearest_grass = env.get_nearest_grass(self.position, self.foraging_radius)
            if nearest_grass is not None:
                # Move toward nearest grass: normalize(grass_pos - rabbit_pos) * speed
                direction = nearest_grass - self.position
                dist = np.linalg.norm(direction)
                
                # If we are effectively AT the grass (eating range)
                if dist < max(2.0, self.speed): 
                    self.energy = min(self.max_energy, self.energy + self.energy_per_grass)
                    env.remove_grass(nearest_grass)
                    env.stats_grass_eaten += 1
                    # We still move a tiny bit or just stay
                    move_vector = np.array([0.0, 0.0])
                else:
                    move_vector = (direction / dist) * self.speed
            else:
                # No grass found, random walk
                angle = np.random.uniform(0, 2 * np.pi)
                move_vector = np.array([np.cos(angle), np.sin(angle)]) * self.speed
        else:
            # Well-fed, random walk only
            angle = np.random.uniform(0, 2 * np.pi)
            move_vector = np.array([np.cos(angle), np.sin(angle)]) * self.speed

        self.move(move_vector, env.bounds)
        self.metabolize()
        self.reproduce(env, None)
        
    def reproduce(self, env, potential_mates):
        from entities import Rabbit
        # Reproduction: E > 50, success probability 0.5, cost 20
        if self.energy > 50.0:
            if potential_mates is None:
                nearby_rabbits = env.get_rabbits_in_radius(self.position, radius=25.0) # Increased 5x
                potential_mates = [r for r in nearby_rabbits if r is not self and r.energy > 50.0]
            
            # Re-filter for strict distance just in case
            potential_mates = [m for m in potential_mates if np.linalg.norm(m.position - self.position) <= 10.0]

            if potential_mates:
                if np.random.random() < 0.5:
                    mate = potential_mates[0] # Pick the first available mate
                    
                    # Spawn new rabbit nearby
                    env.rabbits.append(Rabbit(self.position[0], self.position[1]))
                    env.stats_rabbits_born += 1
                    
                    # Deduct energy from both parents
                    self.energy -= 20.0
                    mate.energy -= 20.0


class Fox(Animal):
    def __init__(self, x, y):
        # Max Energy = 150, Initial Energy = 94, Movement Speed = 15.0, Base Metabolism = 1.0
        super().__init__(x, y, max_energy=150.0, initial_energy=94.0, speed=15.0, base_metabolism=1.0)
        self.vision_range = 30.0 # Decreased from 50.0 for balance
        self.catch_distance = 2.0
        self.hunt_success_prob = 0.8
        self.energy_transfer_efficiency = 0.3

    def detect_prey(self, env) -> list:
        """Queries environment for rabbits within vision R_v = 10.0"""
        return env.get_rabbits_in_radius(self.position, self.vision_range)

    def step(self, env):
        if not self.is_alive:
            return

        # 1. Check Reproduction Mode First
        if self.energy > 95.0:
            # Look for a mate
            nearby_foxes = env.get_foxes_in_radius(self.position, radius=100.0) # Increased 5x from 20
            potential_mates = [f for f in nearby_foxes if f is not self and f.energy > 95.0]
            
            if potential_mates:
                nearest_mate = min(potential_mates, key=lambda f: np.linalg.norm(f.position - self.position))
                direction = nearest_mate.position - self.position
                dist = np.linalg.norm(direction)
                
                if dist < 10.0:
                    move_vector = np.array([0.0, 0.0])
                else:
                    move_vector = (direction / dist) * self.speed
                
                self.move(move_vector, env.bounds)
                self.metabolize()
                self.reproduce(env, potential_mates)
                return

        # 2. Algorithm 2: Predator Pursuit
        prey_list = self.detect_prey(env)
        
        if prey_list:
            # Find nearest prey
            nearest_prey = min(prey_list, key=lambda r: np.linalg.norm(r.position - self.position))
            direction = nearest_prey.position - self.position
            dist = np.linalg.norm(direction)

            # Hunting check: if ||prey_position - fox_position|| < catch radius or speed jump
            if dist < max(self.catch_distance, self.speed):
                if np.random.random() < self.hunt_success_prob:
                    # Catch successful
                    nearest_prey.is_alive = False
                    self.energy += self.energy_transfer_efficiency * nearest_prey.energy
                    self.energy = min(self.max_energy, self.energy)
                    env.stats_rabbits_eaten += 1
                # We reached them, so move distance is just to them (or stay close)
                move_vector = (direction / dist) * min(self.speed, dist) if dist > 0 else np.array([0.0, 0.0])
            else:
                # Pursuit vector: normalize(prey_position - fox_position) * speed
                move_vector = (direction / dist) * self.speed
        else:
            # Random walk
            angle = np.random.uniform(0, 2 * np.pi)
            move_vector = np.array([np.cos(angle), np.sin(angle)]) * self.speed

        self.move(move_vector, env.bounds)
        self.metabolize()
        self.reproduce(env, None)

    def reproduce(self, env, potential_mates):
        from entities import Fox
        # Reproduction: E > 95, success probability 0.75, cost 40
        if self.energy > 95.0:
            if potential_mates is None:
                nearby_foxes = env.get_foxes_in_radius(self.position, radius=25.0) # Increased 5x from 5
                potential_mates = [f for f in nearby_foxes if f is not self and f.energy > 95.0]
            
            potential_mates = [m for m in potential_mates if np.linalg.norm(m.position - self.position) <= 10.0]

            if potential_mates:
                if np.random.random() < 0.75:
                    mate = potential_mates[0]
                    # Spawn new fox nearby
                    env.foxes.append(Fox(self.position[0], self.position[1]))
                    env.stats_foxes_born += 1
                    
                    # Deduct energy from both parents
                    self.energy -= 40.0
                    mate.energy -= 40.0
