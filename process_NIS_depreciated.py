from pathlib import Path
import pandas as pd 

# This script is not well-integrated into a pipeline as this was scrapped in favor of a different pipeline

def combine_csv():
    
    ### Identify files of interest
    current_dir = Path.cwd()
    file_list = sorted([file_path for file_path in current_dir.rglob('*.csv') if file_path.stem[:7] != 'preview'])
    df_export = pd.DataFrame()
    child_dist_index = 'Bin_1Bin_3NearestDistance' # May need to be changed to reflect column name changes

    for file in file_list:
        df = pd.read_csv(file, delimiter = ',')
        try:
            df = df[['TimeLapseIndex', child_dist_index, 'W1-TRITCFillArea']]
        except KeyError:
            continue # handles exception where obeject count csv is indexed or there are modified column names
        
        frame_count = df['TimeLapseIndex'].max()
        file_name = [file.stem for i in range(0,frame_count)]

        total_count = df["TimeLapseIndex"].groupby(df["TimeLapseIndex"], dropna=False).count()
        df_distance_filter = df[(df[child_dist_index] <= 1.6) & (df[child_dist_index] >= 0.2)]
        df_size_filter = df[df["W1-TRITCFillArea"] <= 1.6]
        df_merge = df[(df[child_dist_index] <= 1.6) & (df[child_dist_index] >= 0.2) & (df["W1-TRITCFillArea"] < 1.6)]
        df_filter_rough = df[(df[child_dist_index] <= 2)]

        rough_filter = df_filter_rough[child_dist_index].groupby(df["TimeLapseIndex"]).count()
        fine_filter = df_distance_filter[child_dist_index].groupby(df["TimeLapseIndex"]).count()
        size_filter = df_size_filter[child_dist_index].groupby(df["TimeLapseIndex"]).count()
        both_filter = df_merge[child_dist_index].groupby(df["TimeLapseIndex"]).count()

        data = zip(file_name, total_count, rough_filter, fine_filter, size_filter, both_filter)
        headers = ['file_name', 'total_TRITC_count', 'rough_distance_filter', 'fine_distance_filter', 'size_filter', 'size_distance_filter']
        df_out = pd.DataFrame(data, columns = headers)
        df_export = pd.concat([df_export, df_out])

    df_export.to_csv(f"{current_dir}/../output.csv", index=False)
     
def main():
    combine_csv()

if __name__ == '__main__': 
    main()
