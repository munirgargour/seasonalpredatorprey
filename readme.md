# Seasonal Predator-Prey Simulation

This repository contains the ongoing Milestone 2 implementation of the Seasonal Predator-Prey Simulation. It strictly fulfills the progression requirements by establishing core components without implementing all planned features like advanced multi-seasonal dynamics.

## Project Status
**Currently Implemented:**
- Simulation framework established.
- Core classes (`Animal`, `Rabbit`, `Fox`, `Environment`) implemented.
- **Algorithm 1 Implemented**: Hunger-Driven Foraging (Rabbits search for food when their energy drops below 90% capacity).
- **Algorithm 2 Implemented**: Predator Pursuit (Foxes query for prey within `R_v=30.0` range using `scipy.spatial.KDTree` and pursue).
- **Algorithm 3 Implemented**: Reproduction Mode (Animals seek mates and reproduce when energy exceeds thresholds: >50.0 for Rabbits, >95.0 for Foxes).
- Basic 2D visualization via Matplotlib to verify functionality.

**Still to Come (Milestone 3+):**
- Four-season dynamics (metabolism and growth-rate multipliers depending on Spring/Summer/Fall/Winter).
- Continuous spatial torus wrap-around visuals and long-phase multi-year tracking and analytics charts.

**Changes from M1 Proposal:**
- Instead of building a complex Grid world mapping, spatial queries leverage highly efficient continuous 2D plane KD-trees, solving neighbor-distance bottlenecks immediately without arbitrary grid constraints.

## Installation Instructions

### Dependencies
Require Python 3.8+.
```bash
pip install -r requirements.txt
```

### Setup Guide
1. Clone this repository to your local machine.
2. Install the necessary pip packages via the command above.
3. Verify matplotlib can save to the output directory.

## Usage
Run the main script to start a quick 20-step simulation checking agent dynamics and output logs. Outputs (snapshots) will be saved to the `output/` folder.

```bash
python src/simulation.py --steps 20
```
Then change steps to 1000+ to simulate a year or longer.

*Expected behavior*: The console will print the sizes of the fox and rabbit populations along with grass patches at each timestep, and png screenshots will appear in the output directory.

## Architecture Overview
- **`entities.py`**: Defines object models. `Animal` serves as the abstract base template establishing `energy`, `speed`, `position`, and `metabolism`. `Rabbit` and `Fox` inherit and overwrite behavioral `step()` strategies according to M2 requirements.
- **`environment.py`**: A centralized manager class handling 2D spatial mappings, resource (`grass patches`) generation, and optimized queries utilizing `KDTree`.
- **`simulation.py`**: High-level execution sequence wrapper collecting agent statuses, iterating timesteps, and abstracting data visualizations via matplotlib.
