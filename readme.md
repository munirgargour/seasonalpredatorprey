# Seasonal Predator-Prey Ecosystem Simulation

Agent-based simulation of fox-rabbit dynamics with seasonal environmental forcing and hunger-driven foraging behavior.

## Overview

This project implements a spatially-explicit predator-prey model where populations navigate through annual seasonal cycles. Unlike classical Lotka-Volterra models that assume constant environmental parameters, this simulation incorporates dynamic seasonal effects that alter metabolism rates and resource availability.

### Key Features

- **Four-Season Annual Cycles**: Spring, Summer, Fall, and Winter each impose different environmental constraints
- **Seasonal Modifiers**:
  - Spring: +10% grass regeneration (growing season)
  - Summer: -10% metabolism (reduced thermoregulation costs)
  - Fall: Baseline conditions (transition season)
  - Winter: +10% metabolism, -10% grass growth (harsh conditions)
- **Hunger-Driven Foraging**: Rabbits only seek food when energy < 90%, conserving resources and reducing predation exposure
- **Vision-Based Hunting**: Foxes employ pursuit behavior within 10-unit vision range
- **Energy Budget System**: Individual agents track energy with realistic metabolic costs and trophic transfer (30% efficiency)
- **Continuous 2D Space**: Toroidal 500×500 environment with spatial indexing for efficient neighbor queries

## Research Questions

1. **Seasonal Oscillation Effects**: How do seasonal cycles affect the amplitude and period of predator-prey population oscillations?
2. **Population Stability**: What impact does seasonal forcing have on population stability compared to constant-environment baselines?
3. **Environmental Amplitude Optimization**: What degree of seasonal effect (grass regrowth and metabolism modifiers) best stabilizes populations?

## Agent Specifications

### Rabbits (Prey)
- **Max Energy**: 100 units
- **Metabolism**: 1.0/timestep (×1.1 in winter, ×0.9 in summer)
- **Foraging**: Active when hunger > 10%, gains 10 energy per grass consumption
- **Reproduction**: Requires mate within vision, 50% success rate when energy > 50
- **Movement**: 2.0 units/timestep random walk or food-directed

### Foxes (Predators)
- **Max Energy**: 150 units
- **Metabolism**: 1.5/timestep (×1.1 in winter, ×0.9 in summer)
- **Hunting**: 80% success rate within 2.0 units, 30% energy transfer from prey
- **Reproduction**: Requires mate within vision, 70% success rate when energy > 95
- **Movement**: 3.0 units/timestep pursuit or random walk
- **Vision Range**: 10 units for prey detection

## Implementation

### Technology Stack
- **Language**: Python 3.10+
- **Core Libraries**:
  - NumPy: Numerical operations and random generation
  - SciPy: KD-tree spatial indexing for O(log N) neighbor queries
  - Pandas: Time series data management and seasonal statistics
  - Matplotlib: Population plots, phase portraits, energy dynamics
  - Seaborn: Statistical visualization of seasonal effects

### Project Structure
```
seasonal-predator-prey/
├── src/
│   ├── agents/          # Rabbit and Fox agent classes
│   ├── environment/     # Environment, Season, Grass management
│   └── simulation/      # Main loop, data collection, visualization
├── data/                # CSV outputs and results
├── plots/               # Generated visualizations
├── docs/                # Project documentation
├── requirements.txt     # Python dependencies
└── README.md
```

## Expected Outcomes

Based on theoretical predictions:

1. **Seasonal Population Cycles**: Annual patterns with spring recovery, summer peaks, fall decline, and winter bottlenecks
2. **Increased Oscillation Amplitude**: 30-50% higher peak-to-trough variance compared to non-seasonal baselines
3. **Winter as Limiting Factor**: Populations with insufficient energy reserves entering winter face extinction cascades
4. **Foraging Efficiency**: Hunger-threshold behavior reduces predation mortality by 15-20% during productive seasons
5. **Spatial Clustering**: Winter resource scarcity drives aggregation; summer abundance enables dispersal

## Data Collection

### Metrics Tracked per Timestep
- Population counts (rabbits, foxes)
- Birth/death events with cause classification
- Energy statistics (mean, median, std dev)
- Hunger percentages
- Current season
- Spatial distributions

### Visualizations Generated
- Time series with season-coded backgrounds (green/yellow/orange/blue)
- Phase portraits (predator vs prey populations)
- Energy and hunger dynamics over time
- Seasonal comparison box plots
- Spatial density heatmaps

## Distinguishing Features

This implementation extends beyond basic predator-prey tutorials through:

1. **Seasonal Environmental Dynamics**: Rarely implemented in educational simulations
2. **State-Dependent Behavior**: Hunger-driven foraging creates realistic energy management
3. **Continuous Space**: Vision-based interactions vs. grid-based encounters
4. **Comprehensive Analytics**: Multi-scale data enabling quantitative validation

## Course Information

**CS 4632 Modeling and Simulation**  
Department of Computer Science  
Kennesaw State University  
Spring 2025

**Student**: Munir Gargour  
**GitHub**: https://github.com/munirgargour/seasonalpredatorprey

## Status

- [x] Milestone 1: Project design and UML diagrams
- [ ] Milestone 2: Implementation and validation
- [ ] Milestone 3: Experimentation and analysis
- [ ] Final: Results and conclusions

## References

1. Lotka, A.J. (1925). *Elements of Physical Biology*. Williams & Wilkins.
2. Murray, J.D. (2002). *Mathematical Biology I: An Introduction* (3rd ed.). Springer.
3. Volterra, V. (1926). Fluctuations in the abundance of a species considered mathematically. *Nature*, 118(2972), 558-560.
4. Wilensky, U. (1997). NetLogo Wolf Sheep Predation model. Northwestern University.
