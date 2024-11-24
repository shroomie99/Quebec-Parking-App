"""
Goal: Create a visualization of data to identify where my expectations are different than what is really being displayed.
In terms of regions that permit and restrict parking.

On a map, label signs, street boundaries. Instances that region permit parking and restrict parking.

LOGIC:
(1)
To generate data ... 
-- Using a specific time and date, obtain all signs that are active and all street bounds. 
-- Obtain street boundaries that are associated to the active signs for the scenario
-- Obtain all pairs for active signs with indication if it is a restriction or permission based region

(2)
Send to code the following data:
(for a scenario)
- all active signs
- each pairing for each active sign
- all street bounds
- sign type (restrict or permit)

(3)
Code then ...
- Generates map
- put all sign and sign pairing on map
- generate red line if pairing has sign type of "restrict"
- generate green line if pairing has sign type of "permit"
- generate yellow line if there are signs between the street bounds. ***


"""


import pandas as pd
import json
import time
import ast
import folium
from datetime import datetime, timedelta
from pathlib import Path

# Using data, combine_datasets.csv + scenarios_sign_active_2024-01-01_00-00.csv => Generate a complete file that contains:
# -- rows: contain only active signs
# -- columns: contain variety of parameters (TBD) --> 
# POTEAU_ID_POT, PANNEAU_ID_PAN, DESCRIPTION_RPA, 
# sign_longitude, sign_latitude, rule_type, street_side_coordinate1_lon, street_side_coordinate1_lat,
# street_side_coordinate2_lon, street_side_coordinate2_lat, sign_effective_area_coordinate2, 

# Output result into: test_active_signs_and_streets_data.csv

""" 1. To generate data to visualize on map"""

# File paths
project_root = Path(__file__).resolve().parents[1]  # Assumes 'Code' folder is one level deep within project

scenarios_sign_active_file = project_root / "Datasets" / "scenarios" / "scenarios_sign_active_2024-01-01_04-00.csv"
combine_datasets_file =  project_root / "Datasets" / "combined_datasets.csv"
merged_file =  project_root / "Datasets" / "test_active_signs_and_streets_data.csv"

# Read the required columns from the files
scenarios_sign_active = pd.read_csv(scenarios_sign_active_file, usecols=["PANNEAU_ID_PAN"])
combine_datasets = pd.read_csv(combine_datasets_file, usecols=[
    "POTEAU_ID_POT", "PANNEAU_ID_PAN", "DESCRIPTION_RPA", 
    "sign_longitude", "sign_latitude", "rule_type", 
    "street_side_coordinate1_lon", "street_side_coordinate1_lat", 
    "street_side_coordinate2_lon", "street_side_coordinate2_lat", 
    "sign_effective_area_coordinate1", "sign_effective_area_coordinate2"
])

# Perform the left join
result = pd.merge(
    scenarios_sign_active,
    combine_datasets,
    how="inner",
    on="PANNEAU_ID_PAN"
)

# Save the result to a new CSV file
result.to_csv(merged_file, index=False)

print(f"Data saved to {merged_file}")


""" 2. Transform csv data into sub-datasets, that can be processed by mapping sofware"""
# GOALS:
# - generate list that contains 1 coordinate or 2 coordinate.
# - Case 1 (1 coordinate) : contain 1 coordinate and DESCRIPTION_RPA
# - Case 2 (2 coordinates) : contain 2 coordinates and line color.


# Given test_active_signs_and_streets_data.csv -> 
# - generate list that contains 1 coordinate (in acceptable format) and DESCRIPTION_RPA
#     collect data, transform data, reprovide data
#         1. Data (columns) collected: sign_longitude, sign_latitude, DESCRIPTION_RPA
#         2. Provide the following data to add_signs() : [sign_latitude, sign_longitude , DESCRIPTION_RPA]


# - generate list that contains 2 coordinates (in acceptable format) and line color
#         1. Data (columns) collected: street_side_coordinate1_lat, street_side_coordinate1_lon, street_side_coordinate2_lat, street_side_coordinate2_lon, sign_effective_area_coordinate1, sign_effective_area_coordinate2, rule_type
#         2. Transform data to (
#             street_side_coord1 = (street_side_coordinate1_lat, street_side_coordinate1_lon)
#             street_side_coord2 = (street_side_coordinate2_lat, street_side_coordinate2_lon)
#             sign_effective_area_coord1 = flipped(sign_effective_area_coordinate1)
#             sign_effective_area_coord2 = flipped(sign_effective_area_coordinate2)
#         3. Provide the following data to add_line() : [street_side_coord1, street_side_coord2, sign_effective_area_coord1, sign_effective_area_coord2, rule_type ]
#             Note : 
#                 if street_side_coord, set line to yellow, 
#                 if rule_type is "No Parking", set line to red
#                 if rule_type is "Impact sign directly above", set line to grey
#                 if rule_type is "Parking Allowed", set line to green


# Store lists into test_active_signs_and_streets_transformed.csv

### Case 1 ###

# Load the CSV file
data = pd.read_csv(merged_file)

# Extract the required columns
columns_needed = ["sign_latitude", "sign_longitude", "DESCRIPTION_RPA"]
extracted_data = data[columns_needed]


### Case 2 ### 

# Step 2: Extract required columns
columns_needed = [
    "street_side_coordinate1_lat", "street_side_coordinate1_lon",
    "street_side_coordinate2_lat", "street_side_coordinate2_lon",
    "sign_effective_area_coordinate1", "sign_effective_area_coordinate2", "rule_type"
]

extracted_data2 = data[columns_needed]

# Step 3: Transform data

transformed_data = extracted_data2.copy()
transformed_data.drop(columns=["sign_effective_area_coordinate1", "sign_effective_area_coordinate2"], inplace=True)

transformed_data["street_side_coord1"] = list(zip(
    extracted_data2["street_side_coordinate1_lat"], extracted_data2["street_side_coordinate1_lon"]
))
transformed_data["street_side_coord2"] = list(zip(
    extracted_data2["street_side_coordinate2_lat"], extracted_data2["street_side_coordinate2_lon"]
))

transformed_data["sign_effective_area_coord1"] = extracted_data2["sign_effective_area_coordinate1"].apply(
    lambda x: tuple(reversed(eval(x))) if pd.notna(x) else None
)
transformed_data["sign_effective_area_coord2"] = extracted_data2["sign_effective_area_coordinate2"].apply(
    lambda x: tuple(reversed(eval(x))) if pd.notna(x) else None
)

""" 3. Generate map"""

# Create a map centered around Montreal
latitude, longitude = 45.5017, -73.5673

# Function to add a line to the map
def add_line(map_obj, coord_start, coord_end, color):
    folium.PolyLine(
        locations=[coord_start, coord_end],
        color=color,
        weight=5,  # Thickness of the line
        opacity=0.7
    ).add_to(map_obj)


# Function to add a sign 
def add_signs(map_obj, latitude, longitude, description):
    folium.Marker(
        location=[latitude, longitude],
        popup=description
    ).add_to(map_obj)


# Executed when website detects change in user location
def update_map(latitude, longitude):
    # Update the map with the user's location
    map_montreal = folium.Map(location=[latitude, longitude], zoom_start=16)

    #TODO: Find error. Location values cannot contain NAN + TypeError: 'float' object is not iterable
    # - cant find location with NAN
    # what are my peers in my class doing with there lives now???

    # Add signs to the map
    for _, row in extracted_data.iterrows():
        add_signs(map_montreal, row["sign_latitude"], row["sign_longitude"], row["DESCRIPTION_RPA"])

    print("183")

    # # Step 5: Add lines to the map
    # for _, row in transformed_data.iterrows():
    #     if row["street_side_coord1"] and row["street_side_coord2"]:
    #         # Add street side line (yellow)
    #         add_line(map_montreal, row["street_side_coord1"], row["street_side_coord2"], color="yellow")
    
    #     if row["sign_effective_area_coord1"] and row["sign_effective_area_coord2"]:
    #         # Add effective area line (green)
    #         add_line(map_montreal, row["sign_effective_area_coord1"], row["sign_effective_area_coord2"], color="green")
    # print("194")

    # Save the updated map to an HTML file
    file_path = project_root / 'Datasets' / 'test_map.html'
    map_montreal.save(file_path)

update_map(latitude, longitude)

print("Map generated")