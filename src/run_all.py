"""Run all 10 simulation configurations and write a master index JSON."""
import os
import sys
import json
import glob
import time

# Make sure src/ is on path when called from project root
sys.path.insert(0, os.path.dirname(__file__))

from simulation import Simulation

CONFIG_DIR  = os.path.join(os.path.dirname(__file__), '..', 'configs')
OUTPUT_DIR  = os.path.join(os.path.dirname(__file__), '..', 'output')
INDEX_PATH  = os.path.join(OUTPUT_DIR, 'master_index.json')

def main():
    config_files = sorted(glob.glob(os.path.join(CONFIG_DIR, 'run_*.json')))
    if not config_files:
        print("No config files found in configs/")
        return

    master_index = []
    total_start = time.time()

    for cfg_path in config_files:
        with open(cfg_path) as f:
            config = json.load(f)

        run_id = config.get('run_id', '???')
        desc   = config.get('description', '')
        print(f"\n{'='*60}")
        print(f"Starting Run {run_id}: {desc}")
        print(f"{'='*60}")

        run_start = time.time()
        sim = Simulation(config)
        summary = sim.run(output_dir=OUTPUT_DIR)
        wall_time = time.time() - run_start

        entry = {
            'run_id':         run_id,
            'description':    desc,
            'config_file':    os.path.basename(cfg_path),
            'steps_ran':      sim.timestep,
            'wall_time_sec':  round(wall_time, 2),
            'final_rabbits':  summary['final_rabbits'],
            'final_foxes':    summary['final_foxes'],
            'avg_rabbits':    summary['avg_rabbits'],
            'avg_foxes':      summary['avg_foxes'],
            'extinction_rabbits': summary['extinction_rabbits'],
            'extinction_foxes':   summary['extinction_foxes'],
            'timeseries_csv': f'run_{run_id}_timeseries.csv',
            'summary_json':   f'run_{run_id}_summary.json',
            'config_json':    f'run_{run_id}_config.json',
            'population_png': f'run_{run_id}_population.png',
        }
        master_index.append(entry)

    total_time = time.time() - total_start

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(INDEX_PATH, 'w') as f:
        json.dump({'runs': master_index, 'total_wall_time_sec': round(total_time, 2)}, f, indent=2)

    print(f"\n{'='*60}")
    print(f"All runs complete in {total_time:.1f}s")
    print(f"Master index written to: {INDEX_PATH}")
    print(f"{'='*60}")
    print(f"\n{'Run':^5} {'Description':<45} {'Steps':>6} {'Time':>7} {'R_final':>8} {'F_final':>8}")
    print('-' * 85)
    for e in master_index:
        print(f"{e['run_id']:^5} {e['description']:<45} {e['steps_ran']:>6} "
              f"{e['wall_time_sec']:>6.1f}s {e['final_rabbits']:>8} {e['final_foxes']:>8}")

if __name__ == '__main__':
    main()
