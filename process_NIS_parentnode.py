#!/usr/bin/env python

from pathlib import Path
import pandas as pd 
import numpy as np
import argparse

"""
Associate parent puncta (TRITC) with their nearest child puncta.

Coordinates for parent puncta are stored in file_a and data for child punta are stored in file_b

Processisng colocalization can be done with a different script

"""

def join_parent_child(file_a: Path, file_b: Path):
    """Merges two csv files, output used to calcualte neighbor ratio

    Args:
        file_a (Path): Path to csv file containing parent data (Cy5/TRITC)
        file_b (Path): Path to csv file congtaining parent data (GFP)
    """

    # Loading parent file
    try:
        df_a = pd.read_csv(file_a, sep=',', header=0)
        parent_cols = list(df_a.columns)
    except Exception as e:
        print(f"Error loading or parsing {file_a}: {e}")
        return

    # Load child reference file
    try:
        df_b = pd.read_csv(file_b, sep=',', header=0)
        child_cols = list(df_b.columns)
    except Exception as e:
        print(f"Error loading or parsing {file_b}: {e}")
        return

    # Pull data & join by column names
    df_a.dropna(axis = 0) #remove columns with no near neighbor 
    df_merged = df_a.merge(
        df_b,
        left_on = [parent_cols[0], parent_cols[7]],
        right_on = [child_cols[0], child_cols[2]]
    ) # Joins data based on hard-coded positions because header names can change with different channels

    # Add sanity check for centroid distances here
    print("Dimensions of file a:", df_a.shape)
    print("Dimensions of output file:", df_merged.shape)

    # Output file if everything looks good here. Then send into filtering script for further processing
    print(f"Writing merged particle list to {file_a.stem}_merged.csv")
    df_merged.to_csv(f"{file_a.stem}_merged.csv", index=False)

def calculate_neighbor_ratio(file_a: Path, max_distance: float, max_size: float):
    """Calculates percentage of particles with a neighbor within {threshold} microns

    Args:
        file_a (Path): Path to csv file containing parent data (Cy5/TRITC)
        max_distance (Float): Maximum threshold (in microns) allowed for neighboring puncta to be considered colocalized
        max_size (Float): Maximum size for either channels of puncta to be considered for analysis
    """
    
    # Load merged parent-child file 
    try:
        source = (f"{file_a.stem}_merged.csv")
        df_merged = pd.read_csv(source, sep = ",", header = 0)
        neighbor_cols = list(df_merged.columns)
    except Exception as e:
        print(f"Error loading or parsing {source}: {e}")
        return

    # Hard coded particle size filter (to achieve parity with Fiji pipeline)
    df_merged = df_merged[(df_merged[neighbor_cols[3]] <= 3.0)] # removing large TRITCc puncta
    # if concerned about small background signal being picked up, can add a minimum size here

    # Calculate number of puncta colocalized 
    np_object_counts = df_merged.groupby(neighbor_cols[0])[neighbor_cols[8]].mean().to_numpy()
    np_colocalized = df_merged[(df_merged[neighbor_cols[6]] <= max_distance) & (df_merged[neighbor_cols[3]] <= max_size) & (df_merged[neighbor_cols[14]] <= max_size)].groupby(neighbor_cols[0]).count()[neighbor_cols[6]].to_numpy() # This just works
    colocalization_rate = np_colocalized/np_object_counts
    average_colocalization = round(np.mean(colocalization_rate) * 100, 3)
    data = np.column_stack([np_colocalized, np_object_counts, colocalization_rate])
    np.savetxt(f"{file_a.stem}_colocalization.csv", data, fmt='%.2f', delimiter=",", header="colocalized_puncta, total_puncta, colocalization_rate", comments='')

    # Print results to terminal
    print("\n--- Proximity Analysis Report ---")
    print(f"Particle Coordinate File: {source}")
    print(f"Distance Threshold: {max_distance}")
    print(f"Size Threshold: {max_size}")
    print("--- Results ---")
    print(f"Average Colocalization: {average_colocalization}%")
    print(f"Writing merged particle list to {file_a.stem}_colocalization.csv")
    
def main():
    parser = argparse.ArgumentParser(
        description="Associate the parent puncta information stored in file_a with child puncta information stored in file_b given the child index and frame index"
    )
    parser.add_argument(
        "file_a",
        type=Path,
        help="Relative path to csv containing parent puncta and nearest child index (file_a)."
    )
    parser.add_argument(
        "file_b",
        type=Path,
        help="Relative path to csv containing child information sorted by frame and child index (file_b)."
    )
    parser.add_argument(
        "max_distance",
        type=float,
        help="Maximum distance in microns (um) between parent puncta and their closest child puncta to be considered neighbors",\
        default=2.0
    )
    parser.add_argument(
        "max_size",
        type=float
        help="Maximum size in squared microns of "
        defaut=3.0
    )

    args = parser.parse_args()

    join_parent_child(args.file_a, args.file_b)
    calculate_neighbor_ratio(args.file_a, args.max_distance, args.max_size)

if __name__ == "__main__":
    main()

    ### Debugging
    # parent_child("test_1.csv", "Child_ref_1.csv")
    # join_parent_child(Path(r"Z:\workspace\Kenton\test_new_NIS\test_1.csv"), Path(r"Z:\workspace\Kenton\test_new_NIS\Child_ref_1.csv"))
    # calculate_neighbor_ratio(Path(r"Z:\workspace\Kenton\test_new_NIS\test_1.csv"), 2)

