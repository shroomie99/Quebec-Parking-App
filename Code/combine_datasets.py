###
# combine_datasets.py - Generates an updated CSV that contains the fields below:
# X - street-side id
# X - GPS start and endpoint of street-side

# X - sign id
# X - GPS of sign
# X - sign direction
# X - all sign rules
###

import pandas as pd
import json
from pathlib import Path
import numpy as np
import re

# Find the project root by navigating up from the current script's directory
project_root = Path(__file__).resolve().parents[1]  # Assumes 'Code' folder is one level deep within project

# Specify the path to your CSV file
csv_file_path = project_root / "Datasets" / "signalisation_stationnement.csv"  
mapping_csv_path = project_root / "Datasets" / "sign_to_street_side_mapping.csv"  
simplified_csv_path = project_root / "Datasets" / "simplified_signalisation_stationnement.csv"  
output_csv_path = project_root / "Datasets" / "combined_datasets.csv"  



# # 1) Append sign_to_street_side_mapping.csv to simplified_signalisation_stationnement.csv into file combined_datasets.csv

# # Load the data from both CSV files into DataFrames
# mapping_data = pd.read_csv(mapping_csv_path)
# simplified_data = pd.read_csv(simplified_csv_path)

# # Check if 'COTE_RUE_ID' column exists in simplified_data
# if 'COTE_RUE_ID' not in simplified_data.columns:
#     # Merge the simplified data with the mapping data using PANNEAU_ID_PAN as the key
#     merged_data = pd.merge(simplified_data, mapping_data, on='PANNEAU_ID_PAN', how='left')

#     # Export the merged DataFrame to a new CSV file
#     merged_data.to_csv(output_csv_path, index=False)

#     print(f'Merged CSV data has been saved')
# else:
#     print("COTE_RUE_ID column already exists in the simplified data. Merge operation skipped.")


# # 2) Replace column name from "latitude" and "longitude" to "sign_latitude" and "sign_longitude"

# # Load the CSV file
# data = pd.read_csv(output_csv_path)

# # Rename the 'Latitude' and 'Longitude' columns
# data.rename(columns={'Latitude': 'sign_latitude', 'Longitude': 'sign_longitude'}, inplace=True)

# # Save the updated DataFrame back to CSV
# data.to_csv(output_csv_path, index=False)

# print(f"Columns names replaced in CSV")


# # 3) Replace coordinates from simplified_gbdouble.json into the coordinate columns in combined_datasets.csv

# # Path to the JSON file
# json_file_path = project_root / "Datasets" / "simplified_gbdouble.json"  

# # Load the JSON file
# with open(json_file_path, 'r') as file:
#     json_data = json.load(file)

# # Extract features from JSON and create a DataFrame
# features_data = []
# for feature in json_data['features']:
#     cote_rue_id = feature['properties']['COTE_RUE_ID']
#     street_type_coordinate = feature['geometry']['type']

#     if (street_type_coordinate == 'MultiLineString'):
#         # These type of coordinates are mainly exception cases
#         pass 

#     else:
#         # Extract the first and last set of coordinates for each LineString
#         coordinates_1 = feature['geometry']['coordinates'][0]
#         coordinates_2 = feature['geometry']['coordinates'][-1]
#         features_data.append({
#             'COTE_RUE_ID': cote_rue_id,
#             'street_side_coordinate1_lon': coordinates_1[0],
#             'street_side_coordinate1_lat': coordinates_1[1],
#             'street_side_coordinate2_lon': coordinates_2[0],
#             'street_side_coordinate2_lat': coordinates_2[1]
#         })


# # Convert the list of dictionaries to a DataFrame
# coordinates_df = pd.DataFrame(features_data)

# # Read the CSV data into a DataFrame
# csv_data = pd.read_csv(output_csv_path)

# # Merge the CSV data with the JSON coordinates DataFrame using COTE_RUE_ID as the key
# merged_data = pd.merge(csv_data, coordinates_df, on='COTE_RUE_ID', how='left')

# print("Coordinates replaced in CSV")


# 4) Remove specific erronous text in column "sign_effective_area_coordinate2"
csv_data = pd.read_csv(output_csv_path)

# Function to modify the "sign_effective_area_coordinate2" column
def modify_coordinates(coord):
    if "nan" in str(coord).lower():  # Handle NaN values gracefully
        return None
    
    # Use regex to extract the numeric values and format them
    output_string = re.sub(r'np\.float64\((.*?)\)', r'\1', coord)

    return output_string
    # print(output_string)

# Check if the column exists and apply transformation
if "sign_effective_area_coordinate2" in csv_data.columns:
    csv_data["sign_effective_area_coordinate2"] = csv_data["sign_effective_area_coordinate2"].apply(modify_coordinates)

# Remove rows where "sign_effective_area_coordinate2" is None
csv_data = csv_data.dropna(subset=["sign_effective_area_coordinate2"])

# Save the updated DataFrame to a new CSV file
# output_file = "modified_combined_datasets.csv"
csv_data.to_csv(output_csv_path, index=False)

print(f"Modified CSV file saved to {output_csv_path}")



# # 5) Sort CSV by COTE_RUE_ID & keep only rows that contain DESCRIPTION_REP : "Réel".

# df = merged_data

# # Sort the DataFrame by 'COTE_RUE_ID'
# df_sorted = df.sort_values(by='COTE_RUE_ID', ignore_index=True)

# # Filter rows where 'DESCRIPTION_REP' equals 'Réel'
# df_filtered = df_sorted[df_sorted['DESCRIPTION_REP'] == 'Réel']

# # Export the merged DataFrame into combined_datasets.csv
# df_filtered.to_csv(output_csv_path, index=False)

# print(f'CSV data has been saved to combined_datasets.csv')





