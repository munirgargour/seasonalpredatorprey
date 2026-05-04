# Seasonal Predator-Prey Simulation

This repository contains the final (Milestone 5) implementation of the Seasonal Predator-Prey Simulation. It simulates the population dynamics of rabbits (prey), foxes (predators), and grass (resource) on a toroidal $500 \times 500$ spatial plane across a full simulated year divided into four seasons.

## Project Description
The project is a continuous 2D agent-based model exploring how seasonal variations in resource regeneration and metabolic costs affect the stability of predator-prey cycles. The simulation transitions away from standard grid-based approaches to a continuous toroidal plane utilizing `scipy.spatial.KDTree` for high-performance spatial queries, allowing thousands of agents to interact simultaneously without arbitrary distance artifacts.

**Key Features:**
- **Hunger-Driven Foraging**: Rabbits query KD-trees for the nearest grass patch.
- **Predator Pursuit**: Foxes use KD-trees to identify and chase the nearest rabbit.
- **Reproduction**: Agents reproduce upon accumulating sufficient energy.
- **Seasonal Dynamics**: Metabolism multipliers and grass growth vary dynamically between Spring, Summer, Fall, and Winter.

## Installation Instructions

### Dependencies
Requires Python 3.8+.
```bash
pip install -r requirements.txt
```

### Setup Guide
1. Clone this repository to your local machine.
2. Install the necessary pip packages via the command above.
3. Verify matplotlib can save to the output directory (the `output/` directory must exist or will be created).

## Usage Guide
Run the main script to start a quick 20-step simulation checking agent dynamics and output logs. Outputs (snapshots) will be saved to the `output/` folder.

```bash
python src/simulation.py --steps 20
```
Then change steps to 1000+ to simulate a full year or longer.

Alternatively, to execute the entire batch of predefined configurations, use:
```bash
python src/run_all.py
```

## Parameter Explanations
The simulation can be customized using JSON configuration files located in `configs/`. Key parameters include:
- `num_rabbits`: Initial number of rabbits.
- `num_foxes`: Initial number of foxes.
- `initial_grass`: Initial number of grass patches.
- `spawn_rate`: Base number of new grass patches added per step.
- `seed`: Random seed for reproducibility.
- `steps`: Total simulation steps to run.
- **Seasons (Spring, Summer, Fall, Winter)**: Each has a `metabolism_multiplier` (increases/decreases energy lost per step) and a `grass_multiplier` (scales the `spawn_rate`).

## Example Outputs
When running a simulation, the console will print the sizes of the fox and rabbit populations along with grass patches at each timestep. In the `output/` folder, you will find:
- **`run_XXX_timeseries.csv`**: A step-by-step breakdown of populations and births.
- **`run_XXX_summary.json`**: Aggregate statistics including maximum populations and extinction flags.
- **`run_XXX_population.png`**: A two-panel chart displaying rabbit/fox population dynamics over time, with shaded backgrounds indicating the changing seasons.

## Architecture Overview
- **`entities.py`**: Defines object models. `Animal` serves as the abstract base template establishing `energy`, `speed`, `position`, and `metabolism`. `Rabbit` and `Fox` inherit and overwrite behavioral strategies.
- **`environment.py`**: A centralized manager handling 2D spatial mappings, resource generation, and optimized queries utilizing `KDTree`.
- **`simulation.py`**: High-level execution sequence wrapper collecting agent statuses, iterating timesteps, and abstracting data visualizations via Matplotlib.
- **`run_all.py`**: Iterates over all configurations and generates a master output index.
