#!/usr/bin/env python

import pandas as pd
import argparse
from pathlib import Path

# config
pixel_scalar = 80/13 # constant determined by the pixel size of the microscope

def export_particle_coordinates(source: Path, lower_bound: float, upper_bound: float, puncta_size: float):
    try:
        file = pd.read_csv(source)
        source_dir = Path(source).parent
    except Exception as e:
        print(f"Error loading or parsing {source}: {e}")
        return
    
    distance_filter = file[(file['Distance'] <= upper_bound) & (file["Distance"] >= lower_bound)]
    area_col = list(file.filter(regex = 'Area').columns)
    size_filter = distance_filter[(distance_filter[area_col[0]] < puncta_size)]    
    df_out = size_filter[['TimeLapseIndex', 'XM', 'YM', area_col[0],'Distance', 'Mean', 'Neighbor_XM', 'Neighbor_YM', 'Neighbor_Area']].copy()
    df_out = df_out.rename(columns={'Mean': 'MeanIntensity'})
    df_out['XM'] = df_out['XM'] * pixel_scalar
    df_out['YM'] = df_out['YM'] * pixel_scalar
    df_out['Neighbor_XM'] = df_out['Neighbor_XM'] * pixel_scalar
    df_out['Neighbor_YM'] = df_out['Neighbor_YM'] * pixel_scalar
    df_out.to_csv(f"{source_dir}/coords_filtered.csv", index=False) 

def main():
    parser = argparse.ArgumentParser(
    description="Export the coordinates of particles from a csv (source) that have a "
                "neighbor between two distances (lower_bound & upper_bound).",
    formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "source", 
        type=Path, 
        help="Path to the particle file (source).\n"
             "A text file with particle data including XM, YM, and Area columns."
    )
    parser.add_argument(
        "lower_bound", 
        type=float, 
        default=0.2,
        help="The minimum distance for two neighbors to be selected."
    )
    parser.add_argument(
        "upper_bound", 
        type=float, 
        default=1.6
        help="The maximum distance for two neighbors to be selected."
    )
    parser.add_argument(
        "puncta_size",
        type=float,
        default=1,
        help="The maximum size of a puncta to be selected"
    )

    args = parser.parse_args()

    export_particle_coordinates(args.source, args.lower_bound, args.upper_bound, args.puncta_size)

if __name__ == "__main__":
    main()
