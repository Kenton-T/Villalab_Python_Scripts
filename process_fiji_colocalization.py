import argparse
import sys
from neighbor_ratio_fiji import calculate_neighbor_ratio # assumes that this file is located in the same directory as neighbor_ratio_edit.py
from pathlib import Path
import pandas as pd 
import numpy as np

# Add the parent directory of star_handler_v2 to the system path
# This allows importing from the star_handler package
# Assumes the script is run from the root of the project or the python_scripts directory
# script_dir = Path(__file__).resolve().parent
# project_root = script_dir.parent
# sys.path.append(str(project_root))

try:
    from star_handler_v2.star_handler.core import matrix_math
except ImportError:
    print("Error: Could not import the 'star_handler' package.")
    print("Please ensure that 'star_handler_v2' is in the correct parent directory or installed.")
    sys.exit(1)


# assumes that you run your script in the directory of the .txt files
def looped_export(threshold: float):
    #locating files with the proper naming convention and file type and saves the file name without extension
    file_names = [file.name for file in Path.cwd().iterdir() if Path(file).suffix  == '.txt' and Path(file).stem[0:3] == "ch1" and Path(file).stem[-4:] != "_out"]

    #calculates neighbor ratio
    summary_data = [calculate_neighbor_ratio(Path(i), Path("ch2"+i[3:]), threshold) for i in file_names] #list of calculated colocalization
    neighbor_coords = [files.name for files in Path.cwd().iterdir() if Path(files).suffix == '.txt' and Path(files).stem[-4:] == "_out"]
    summary_header = ["frame", "neighbor_count", "total_count", "percent_colocalized"]
    df_summary = pd.DataFrame(summary_data)
    df_coords = [pd.read_csv(files) for files in neighbor_coords]
    df_final = pd.concat(df_coords, ignore_index=True)
    df_final.to_csv("particles.csv", index = False)
    df_summary.to_csv("summary.csv", index = False, header = summary_header)

def main():
    parser = argparse.ArgumentParser(
    description="Loop the neighbor_ratio script over a series of txt files found in the "
                "directory. See neighbor_ratio_edit.py",
    formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "threshold", 
        type=float, 
        const=2,
        help="The distance threshold in microns to consider a particle a neighbor."
    )

    args = parser.parse_args()

    looped_export(args.threshold)

if __name__ == '__main__':
    main()