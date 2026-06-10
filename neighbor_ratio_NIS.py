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
        df_a = pd.read_csv(file_a, sep=',', header=0)
    except Exception as e:
        print(f"Error loading or parsing {file_a}: {e}")
        return

    print(f"Loading coordinates from Set B: {file_b}")
    try:
        df_b = pd.read_csv(file_b, sep=',', header=0)
    except Exception as e:
        print(f"Error loading or parsing {file_b}: {e}")
        return
    
    # Renaming headers from NIS elements output
    for dataframes in [df_a, df_b]:
        headers = list(dataframes.filter(regex="CenterX|CenterY").columns)
        for i in headers:
            if i[-1:] == "X":
                dataframes.rename(columns={i: "XM"}, inplace=True)
            if i[-1:] == "Y":
                dataframes.rename(columns={i: "YM"}, inplace=True)

    max_frame = df_a['TimeLapseIndex'].max()
    temp_dict = {}
    df_out = pd.DataFrame()
    for i in range(0,max_frame):
        df_a1 = df_a[df_a['TimeLapseIndex'] == i+1].copy()
        coords_a = df_a1[['TimeLapseIndex', 'XM', 'YM']].to_numpy()
        df_b1 = df_b[df_b['TimeLapseIndex'] == i+1].copy()
        coords_b = df_b1[['TimeLapseIndex', 'XM', 'YM']].to_numpy()
        distances = matrix_math.find_nearest_neighbor_distances(coords_a, coords_b)
        
        df_a1['Distance'] = distances
        df_out = pd.concat([df_out, df_a1], ignore_index=True)
        has_neighbor = distances <= threshold
        neighbor_count = int(np.sum(has_neighbor))
        total_count = len(coords_a)

        if total_count > 0:
            percentage = (neighbor_count / total_count) * 100
        else:
            percentage = 0.0
        temp_dict[i+1] = (percentage, neighbor_count, total_count)
        i = i+1

    df = pd.DataFrame.from_dict(temp_dict, orient='index')
    df.columns = ['Percent_Colocalized', 'Particles_Colocalized', 'Total_Particles']
    df.to_csv("summary.csv")
    df_out.to_csv("output.csv")
    ParticlesColoc = df['Particles_Colocalized'].sum()
    TotalParticles = df['Total_Particles'].sum()
    percentage_output = ParticlesColoc / TotalParticles * 100

    print("\n--- Proximity Analysis Report ---")
    print(f"Set A File: {file_a.name}")
    print(f"Set B File: {file_b.name}")
    print(f"Distance Threshold: {threshold} microns")
    print("--- Results ---")
    print(f"Particles in Set A with a neighbor in Set B: {ParticlesColoc} / {TotalParticles}")
    print(f"Percentage: {percentage_output:.2f}%")

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
