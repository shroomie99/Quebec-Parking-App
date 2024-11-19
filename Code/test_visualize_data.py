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

#### (3) ####

import pandas as pd
import json
import time
import ast
import folium
from datetime import datetime, timedelta

from pathlib import Path





"""Load data"""

project_root = Path(__file__).resolve().parents[1]  # Assumes 'Code' folder is one level deep within project

# Specify the path to the .txt file
input_file_path_coverage_region = "123" #TODO: Update to correct path
input_file_path_sign_pairing = "123" #TODO: Update to correct path

# Read the contents of the file
with open(input_file_path_sign_pairing, 'r') as file:
    signs = file.read()


# Read the contents of the file
with open(input_file_path_coverage_region, 'r') as file:
    content = file.read()

# Convert the string back to a list of tuples using ast.literal_eval
legal_parking_regions = ast.literal_eval(content)

# Swap latitude and longitude for each coordinate
swapped_parking_regions = [
    ((lat1, lon1), (lat2, lon2))
    for ((lon1, lat1), (lon2, lat2)) in legal_parking_regions
]

coordinate_ranges = swapped_parking_regions

"""Generate map"""

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

# Function to add a blue dot at the user's location
def add_user_location(map_obj, latitude, longitude):
    folium.CircleMarker(
        location=[latitude, longitude],
        radius=7,  # Size of the dot
        color='blue',  # Blue outline
        fill=True,
        fill_color='blue',  # Fill the dot with blue
        fill_opacity=0.9
    ).add_to(map_obj)

# Function to add a flag of sign 
def add_signs(map_obj, latitude, longitude):
    folium.CircleMarker(
        location=[latitude, longitude],
        radius=7,  # Size of the dot
        color='red',  # Blue outline
        fill=True,
        fill_color='blue',  # Fill the dot with blue
        fill_opacity=0.9
    ).add_to(map_obj)


# Executed when website detects change in user location
def update_map(latitude, longitude):
    # Update the map with the user's location
    map_montreal = folium.Map(location=[latitude, longitude], zoom_start=16)

    # Add the blue dot to represent the user's location
    add_user_location(map_montreal, latitude, longitude)

    add_signs(map_montreal, signs[0], signs[1])

    # Add lines to the map for each coordinate range
    for start, end, color in coordinate_ranges:
        add_line(map_montreal, start, end, color)

    # Save the updated map to an HTML file
    file_path = project_root / 'Datasets' / 'montreal_highlighted_map.html'
    map_montreal.save(file_path)

update_map(latitude, longitude)

print("Map generated")