import sys
import numpy as np
import matplotlib.pyplot as plt
import argparse
from environment import Environment

class Simulation:
    def __init__(self, num_rabbits=100, num_foxes=5, initial_grass=200):
        self.env = Environment(width=500.0, height=500.0)
        # Populate initial entities
        self.env.populate(num_rabbits=num_rabbits, num_foxes=num_foxes, initial_grass=initial_grass)
        
        self.timestep = 0
        
        # Data tracking
        self.history_rabbits = []
        self.history_foxes = []
        
    def step(self):
        # 1. Agent updates
        for rabbit in self.env.rabbits:
            rabbit.step(self.env)
            
        for fox in self.env.foxes:
            fox.step(self.env)
            
        # 2. Grass regeneration
        self.env.step_grass()
        
        # 3. Cleanup logic (remove dead actors)
        self.env.cleanup_dead_agents()
        
        # 4. Data collection
        self.history_rabbits.append(len(self.env.rabbits))
        self.history_foxes.append(len(self.env.foxes))
        
        self.timestep += 1
        print(f"Timestep {self.timestep}: R={len(self.env.rabbits)} F={len(self.env.foxes)} G={len(self.env.grass_patches)} | "
              f"Eaten (G:{self.env.stats_grass_eaten}, R:{self.env.stats_rabbits_eaten}) | "
              f"Born (R:{self.env.stats_rabbits_born}, F:{self.env.stats_foxes_born})")
        
    def render(self, save_path=None):
        plt.figure(figsize=(8, 8))
        plt.xlim(0, self.env.bounds[0])
        plt.ylim(0, self.env.bounds[1])
        plt.title(f"Seasonal Predator-Prey Simulation - Timestep {self.timestep}")
        
        # Plot Grass
        if len(self.env.grass_patches) > 0:
            plt.scatter(self.env.grass_patches[:, 0], self.env.grass_patches[:, 1], c='green', alpha=0.5, s=10, label='Grass')
            
        # Plot Rabbits
        rabbit_coords = np.array([r.position for r in self.env.rabbits if r.is_alive])
        if len(rabbit_coords) > 0:
            plt.scatter(rabbit_coords[:, 0], rabbit_coords[:, 1], c='blue', s=20, label='Rabbits')
            
        # Plot Foxes
        fox_coords = np.array([f.position for f in self.env.foxes if f.is_alive])
        if len(fox_coords) > 0:
            plt.scatter(fox_coords[:, 0], fox_coords[:, 1], c='red', marker='x', s=50, label='Foxes')
            
        plt.legend(loc='upper right')
        
        if save_path:
            import os
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path)
            print(f"Saved snapshot to {save_path}")
        plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Seasonal Predator-Prey Simulation (M2).")
    parser.add_argument("--steps", type=int, default=1000, help="Number of timesteps to run (1000 = 4 seasons).")
    args = parser.parse_args()
    
    sim = Simulation()
    
    # Save frame 0
    sim.render(save_path=f"output/frame_0.png")
    
    for _ in range(args.steps):
        sim.step()
        
        # Output frames at regular intervals (approx 10 frames total)
        interval = max(1, args.steps // 10)
        if sim.timestep % interval == 0 or sim.timestep == args.steps:
            sim.render(save_path=f"output/frame_{sim.timestep}.png")
