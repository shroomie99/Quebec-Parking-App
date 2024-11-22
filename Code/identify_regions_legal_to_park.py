"""
Find regions that a vehicle can have legal parking given a scenario (time, date).
- Generate cases and the respective actions based on where each sign restricts on a street.
- Output a .txt file containing:
    - Output: Tuple List of legal parking regions [(start_coordinate_1, end_coordinate_1),..., (start_coordinate_z, end_coordinate_z)]

(1) For each scenarios (input variations of date, time). 
    (b) Determine region that is legal to park. 
    Input: scenarios_sign_active.csv + combined_dataset.csv
    Output: Into a file called: {scenario_time}_{scenario_date}_map.txt. Containing only a list legal parking regions, i.e. [start_coordinate,end_coordinate]

"""

import pandas as pd
import ast

from pathlib import Path

# Find the project root by navigating up from the current script's directory
project_root = Path(__file__).resolve().parents[1]  # Assumes 'Code' folder is one level deep within project

# Specify the path to your CSV file
csv_file_path = project_root / "Datasets" / "signalisation_stationnement.csv"  


def is_between_tuples(input_value, tuple1, tuple2):
    x, y = input_value
    x1, y1 = tuple1
    x2, y2 = tuple2

    return x1 <= x <= x2 and y1 <= y <= y2


# Convert into a coordinates into coordinate in format of tuple string
def convert_to_tuple(street_side_coordinate1_lon, street_side_coordinate1_lat, street_side_coordinate2_lon, street_side_coordinate2_lat):
    # Create tuples for each set of coordinates with string formatting
    coord1 = (street_side_coordinate1_lon, street_side_coordinate1_lat)
    coord2 = (street_side_coordinate2_lon, street_side_coordinate2_lat)
    
    return coord1, coord2

# Convert coordinate strings to float tuples.
def parse_coordinates(coord):
    return (float(coord[0]), float(coord[1]))
 

def initiate_new_bound_in_COTE_RUE_ID(row, legal_parking_areas, current_bounds):

    # Update legal_parking_areas with list of valid parking areas from current_bounds
    legal_parking_areas.extend(current_bounds) 
    
    street_start = parse_coordinates(row['street_side_coord1'])
    street_end = parse_coordinates(row['street_side_coord2'])
    sign_start = parse_coordinates(ast.literal_eval(row['sign_effective_area_coordinate1']))
    sign_end = parse_coordinates(ast.literal_eval(row['sign_effective_area_coordinate2']))
    # print("a", type(street_start))
    # print("b", type(street_end))
    # print("c", type(sign_start))
    # print("d", type(sign_end))

    current_bounds = []

    # Evalutes whether parking sign is for whole street or not.
    if row['rule_type'] == "No Parking":

        # Check if sign restricts parking everywhere on this street. I.e. 0 boundaries
        if street_start == sign_start and sign_end == street_end: 
            current_bounds = ["whole street unparkable"] # If "whole street unparkable" - means all regions in from street_start and street_end should be eliminated

        # Check if street_start is equal to the sign region start. I.e. only 1 boundary
        elif street_start == sign_start :
            region2 = (sign_end, street_end)
            current_bounds = [region2]

        # Check if street_end is equal to the sign region end. I.e. only 1 boundary
        elif sign_end == street_end:
            region1 = (street_start, sign_start)
            current_bounds = [region1]
            
        # Therefore, parking is restricted in between street_start and street_end. I.e. 2 boundaries
        else:
            region1 = (street_start, sign_start)
            region2 = (sign_end, street_end)
            current_bounds = [region1, region2]

    return current_bounds


def is_sign_encapsulating_region(sign_tuple, region_tuple):
    '''Check if the sign_tuple encapsulates the region_tuple'''

    # Unpack coordinates
    (sign_min_lon, sign_min_lat), (sign_max_lon, sign_max_lat) = sign_tuple
    (region_min_lon, region_min_lat), (region_max_lon, region_max_lat) = region_tuple
    
    # Check if sign_tuple encapsulates region_tuple
    return (sign_min_lon <= region_min_lon and sign_max_lon >= region_max_lon and
            sign_min_lat <= region_min_lat and sign_max_lat >= region_max_lat)



def calculate_legal_parking_areas(df_whole):
    """
    Algorithm to find free parking areas 

    street_side_coord1: Tuple of start coordinates (longitude, latitude) for the street side.
    street_side_coord2: Tuple of end coordinates (longitude, latitude) for the street side.
    sign_effective_area_coordinate1: List of tuples of start coordinates for each sign's effective area.
    sign_effective_area_coordinate2: List of tuples of end coordinates for each sign's effective area.
    COTE_RUE_ID: List of integers identifying groups of signs associated with each street side.

    Returns a list of tuples representing legal parking coordinates.
    """
        
    # Store results
    legal_parking_areas = []

    previous_row_COTE_RUE_ID = None # Identifies street_edge. Used for checking COTE_RUE_ID field is same or different
    current_bounds = [] # Temp variable used in each iteration containing legal parking spaces for a street edge.

    # Iterate over whole table
    for index, row in df_whole.iterrows():
        current_row_COTE_RUE_ID = row['COTE_RUE_ID'] 
        
        # First iteration
        if previous_row_COTE_RUE_ID is None:
            current_bounds = initiate_new_bound_in_COTE_RUE_ID(row, legal_parking_areas, current_bounds)

        # Second and future iterations. 
        else:
        
            # Different COTE_RUE_ID value from previous iteration.
            if current_row_COTE_RUE_ID != previous_row_COTE_RUE_ID:
                current_bounds = initiate_new_bound_in_COTE_RUE_ID(row, legal_parking_areas, current_bounds)

                # Move to next DIFFERENT COTE_RUE_ID
                if "whole street unparkable" in current_bounds:
                    
                    # Update the previous_value for the next iteration
                    previous_row_COTE_RUE_ID = current_row_COTE_RUE_ID
                    continue

            # Same COTE_RUE_ID value from previous iteration
            else:
                # Continue to apply sign variables to current street_side_coords
                sign_start = parse_coordinates(ast.literal_eval(row['sign_effective_area_coordinate1']))
                sign_end = parse_coordinates(ast.literal_eval(row['sign_effective_area_coordinate2']))

                # cases to check regarding current_bounds elements
                # case 1: whole street unparkable
                if "whole street unparkable" in current_bounds:
                    previous_row_COTE_RUE_ID = current_row_COTE_RUE_ID
                    continue

                # case 2: remove duplicate tuples in list
                current_bounds = list(dict.fromkeys(current_bounds))                

                # case 3: remove a region that encapsulates a sub-region in list. Remove the larger region. 
                # current_bounds = remove_encapsulating_tuples(current_bounds)

                # case 4: checks that current_bounds is not empty
                if current_bounds: 
                    
                    future_bounds = []  # List to store the updated regions

                    for index, region in enumerate(current_bounds):
                        # Relabel region coordinates
                        region_start = region[0]
                        region_end = region[1]

                        # Check both signs, whether they are between a valid street region(s)
                        sign_start_check = is_between_tuples(sign_start, region_start, region_end)
                        sign_end_check = is_between_tuples(sign_end, region_start, region_end)

                        # Case 5: Sign area covers a region larger than current region.
                        if is_sign_encapsulating_region((sign_start,sign_end), (region_start,region_end)):
                            continue # "continue" removes region from list

                        # Case 1: Sign area covers part of the center of the region
                        if sign_start_check and sign_end_check:
                            region1 = (region_start, sign_start)
                            region2 = (sign_end, region_end)
                            future_bounds.append(region1)
                            future_bounds.append(region2)

                        # Case 2: Sign area covers part of the start of the region
                        elif sign_start_check and not sign_end_check:
                            region_new = (sign_start, region_end)
                            future_bounds.append(region_new)

                        # Case 3: Sign area covers part of the end of the region
                        elif sign_end_check and not sign_start_check:
                            region_new = (region_start, sign_start)
                            future_bounds.append(region_new)

                        # Case 4: No overlap, keep the region unchanged
                        elif not sign_end_check and not sign_start_check:
                            future_bounds.append(region)

                        else:
                            pass

                    # Replace current_bounds with the updated future_bounds
                    current_bounds = future_bounds

        # Update the previous_value for the next iteration
        previous_row_COTE_RUE_ID = current_row_COTE_RUE_ID
    
    return legal_parking_areas


def execute_me(scenario_file_csv_path, tmp_scenario_date, tmp_scenario_time):
    ## Logic to find and generate a .txt of legal parking spaces for an individual scenario ##
    combined_datasets_csv_path = project_root / "Datasets" / "combined_datasets.csv"  

    scenario_file_csv_path = scenario_file_csv_path

    # Load the data from CSV files into DataFrames
    combined_df = pd.read_csv(combined_datasets_csv_path, low_memory=False)
    scenarios_df = pd.read_csv(scenario_file_csv_path)

    # 
    # Performs a left join on the two dataframes using PANNEAU_ID_PAN.
    joined_df = pd.merge(scenarios_df, combined_df, on='PANNEAU_ID_PAN', how='left')
        
    ## This line is used for testing purposes ##
    # joined_df = pd.read_csv(r'C:\Users\Benjamin\Desktop\Python Projects\Quebec Parking App\Datasets\sample_data.csv', low_memory=False)

    # print(joined_df.columns.tolist())

    # Remove rows where any of the specified columns are empty
    columns_to_check = ['street_side_coordinate1_lon', 'street_side_coordinate1_lat', 'street_side_coordinate2_lon', 'street_side_coordinate2_lat']
    joined_df = joined_df.dropna(subset=columns_to_check)

    selected_columns = [
        'scenario_time',
        'scenario_date',
        'PANNEAU_ID_PAN',
        'COTE_RUE_ID',
        'sign_effective_area_coordinate1',
        'sign_effective_area_coordinate2',
        'street_side_coordinate1_lon',
        'street_side_coordinate1_lat',
        'street_side_coordinate2_lon',
        'street_side_coordinate2_lat',
        'rule_type'
    ]


    # Select the relevant columns and Converts float coordinates into Tuple
    joined_df = joined_df.loc[:, selected_columns]
   
    joined_df['street_side_coord1'], joined_df['street_side_coord2'] = zip(*joined_df.apply(
        lambda row: convert_to_tuple(
            row['street_side_coordinate1_lon'],
            row['street_side_coordinate1_lat'],
            row['street_side_coordinate2_lon'],
            row['street_side_coordinate2_lat']
        ), axis=1))

    # Calculate legal parking regions
    legal_parking_regions = calculate_legal_parking_areas(joined_df)
    
    # Remove 'whole street unparkable' from the list
    legal_parking_regions = [item for item in legal_parking_regions if item != 'whole street unparkable']

    # Generate unique time and date based file name
    file_name = f"map_{tmp_scenario_date}__{tmp_scenario_time}.txt"
    
    output_file_path = project_root / "Datasets" / "maps" / file_name

    # Write the raw contents of the list to the file without modification
    with open(output_file_path, 'w') as file:
        file.write(str(legal_parking_regions))

    print('Generated a file. For a scenario, with the list of legal parking regions')


def main():
    ## Loop through each scenario date and time within scenarios folder. Generate a .txt of legal parking spaces for each scenario. ##
    # Given folder path. Read title of each file. Extract scenario_date and scenario_time from title. Then go onto next file in folder.

    import os
    import re

    # Define the folder path
    folder_path = project_root / "Datasets" / "scenarios"  

    # Define a regular expression pattern to extract scenario_date and scenario_time
    pattern = r'scenarios_sign_active_(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2})\.csv'

    # Loop through the files in the folder
    for filename in os.listdir(folder_path):
        # Check if the file matches the expected pattern
        match = re.search(pattern, filename)
        if match:
            scenario_date = match.group(1)
            scenario_time = match.group(2)

            print(f"File: {filename}")
            print(f"Scenario Date: {scenario_date}")
            print(f"Scenario Time: {scenario_time}\n")
            
            scenario_path = project_root / "Datasets" / "scenarios" / f"scenarios_sign_active_{scenario_date}_{scenario_time.replace(':', '-')}.csv"
            execute_me(scenario_path, scenario_date, scenario_time)
        else:
            print(f"File {filename} does not match the expected pattern.\n")

    print("All scenarios executed")
    

if __name__ == "__main__":
    main()