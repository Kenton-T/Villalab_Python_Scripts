#!/usr/bin/env python

import argparse
import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Add the parent directory of star_handler_v2 to the system path
# This allows importing from the star_handler package
# Assumes the script is run from the root of the project or the python_scripts directory
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.append(str(project_root))

try:
    from star_handler_v2.star_handler.core import matrix_math
except ImportError:
    print("Error: Could not import the 'star_handler' package.")
    print("Please ensure that 'star_handler_v2' is in the correct parent directory or installed.")
    sys.exit(1)

def calculate_neighbor_ratio(file_a: Path, file_b: Path, threshold: float):
    """
    Calculates the ratio of particles in file_a that have a neighbor in file_b.

    Args:
        file_a (Path): Path to a text file with particle data (Set A).
        file_b (Path): Path to a text file with particle data (Set B).
        threshold (float): The distance threshold in microns.
    """
    print(f"Loading coordinates from Set A: {file_a}")
    try:
        df_a = pd.read_csv(file_a, sep=r'\s+', header=0)
        coords_a = df_a[['XM', 'YM']].to_numpy()
    except Exception as e:
        print(f"Error loading or parsing {file_a}: {e}")
        return

    print(f"Loading coordinates from Set B: {file_b}")
    try:
        df_b = pd.read_csv(file_b, sep=r'\s+', header=0)
        coords_b = df_b[['XM', 'YM']].to_numpy()
    except Exception as e:
        print(f"Error loading or parsing {file_b}: {e}")
        return

    print("Calculating nearest neighbor distances...")
    distances, neighbor_index = matrix_math.find_nearest_neighbor_distances(coords_a, coords_b)
    has_neighbor = distances <= threshold
    neighbor_count = int(np.sum(has_neighbor))
    total_count = len(coords_a)

    # To add additional columns to the export, add additional columns here
    df_a['Distance'] = distances
    df_a['Neighbor_XM'] = coords_b[neighbor_index, 0]
    df_a['Neighbor_YM'] = coords_b[neighbor_index ,1]
    df_a['Neighbor_Area'] = df_b[neighbor_index, 'Area']
    file_a_name = file_a.name  #grabs frame position from movie name
    end_index = file_a_name.find("_particles")
    frame_index = file_a_name[4:end_index]
    df_a['TimeLapseIndex'] = frame_index

    if total_count > 0:
        percentage = (neighbor_count / total_count) * 100
    else:
        percentage = 0.0

    print("\n--- Proximity Analysis Report ---")
    print(f"Set A File: {file_a.name}")
    print(f"Set B File: {file_b.name}")
    print(f"Distance Threshold: {threshold} microns")
    print("--- Results ---")
    print(f"Particles in Set A with a neighbor in Set B: {neighbor_count} / {total_count}")
    print(f"Percentage: {percentage:.2f}%")
    print(f"Saving results to {file_a.stem}_out.txt")
    df_a.to_csv(f"{file_a.stem}_out.txt", index = False)
    return(frame_index, neighbor_count, total_count, percentage)

def main():
    parser = argparse.ArgumentParser(
        description="Calculate the ratio of particles in one coordinate list (A) that have a "
                    "neighbor in a second list (B) within a given distance threshold.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "file_a", 
        type=Path, 
        help="Path to the primary coordinate file (Set A).\n"
             "A text file with particle data including XM and YM columns."
    )
    parser.add_argument(
        "file_b", 
        type=Path, 
        help="Path to the secondary coordinate file (Set B).\n"
             "A text file with particle data including XM and YM columns."
    )
    parser.add_argument(
        "threshold", 
        type=float, 
        help="The distance threshold in microns to consider a particle a neighbor."
    )

    args = parser.parse_args()

    calculate_neighbor_ratio(args.file_a, args.file_b, args.threshold)

if __name__ == "__main__":
    main()
