"""
(1) Given user input data, which includes the following,
Inputs: 
- current_date, 
- current_time, 
- user_parking_duration
- user_location
- user_resident_only_parking_sticker (optional)

(2) Identify which .txt or .npy file to use, which is based on current_date and current_time, (and that is generated from identify_regions_legal_to_park.py)
(3) Generate a map using the data file
(4) Display the map on a webpage

"""

# Given user inputs, generate geojson that can be used to map where user can park and not park
########################

import pandas as pd
import json
import time
import ast
import folium
from datetime import datetime, timedelta
from branca.element import Element

from pathlib import Path

# Determine the base directory of the script
base_dir = Path(__file__).parent.parent

file_path = base_dir / 'Datasets' / 'montreal_highlighted_map.html'

## (1) Identify file to load, using user_input
# Get the current date and time in proper format

project_root = Path(__file__).resolve().parents[1]  # Assumes 'Code' folder is one level deep within project

# Function to get the first occurrence of the same weekday in the month
def get_date(now):
    # Get the current year, month, and weekday
    year = now.year
    month = now.month
    weekday = now.weekday()  # Monday is 0 and Sunday is 6
    
    # Create a date for the first day of the month
    first_day_of_month = datetime(year, month, 1)
    
    # Find the first occurrence of the same weekday
    days_to_add = (weekday - first_day_of_month.weekday()) % 7
    first_weekday_date = first_day_of_month + timedelta(days=days_to_add)
    
    # Return the formatted date
    return first_weekday_date.strftime("%Y-%m-%d")

# Function to floor the time to the nearest 2-hour interval
def get_time(now):
    # Floor the time to the nearest 2-hour interval
    floored_hour = (now.hour // 2) * 2
    floored_time = now.replace(hour=floored_hour, minute=0, second=0, microsecond=0)
    
    # Return the formatted time
    return floored_time.strftime("%H:%M")


# Get the current date and time
now = datetime.now()

# Get the first weekday date and floored time
scenario_date = get_date(now)
scenario_time = get_time(now).replace(":", "-")

print(scenario_date)
print(scenario_time)


## (3) Load and transform data to generate the map ##

## Load the Coordinates ##
# Specify the path to the .txt file
input_file_path = project_root / "Datasets" / "maps" / f"map_{scenario_date}__{scenario_time}.txt"

# Read the contents of the file
with open(input_file_path, 'r') as file:
    content = file.read()

# Convert the string back to a list of tuples using ast.literal_eval
legal_parking_regions = ast.literal_eval(content)


# Swap latitude and longitude for each coordinate
swapped_parking_regions = [
    ((lat1, lon1), (lat2, lon2))
    for ((lon1, lat1), (lon2, lat2)) in legal_parking_regions
]

coordinate_ranges = swapped_parking_regions

## (4) Generate a map with highlighted region, with where user can park ##

# Create a map centered around Montreal
latitude, longitude = 45.5017, -73.5673

# Function to add a line to the map
def add_line(map_obj, coord_start, coord_end):
    folium.PolyLine(
        locations=[coord_start, coord_end],
        color='green',
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

def add_legend(map_obj):
    
    # Define the HTML for the legend
    legend_html = '''
    <div style="
        position: fixed; 
        bottom: 20px; left: 20px; width: 120px; height: auto; 
        background-color: white; border:1px solid grey; z-index:9999; 
        font-size:12px; padding: 5px; border-radius:5px;
    ">
        <b>Legend</b><br>
        <div style="display: flex; align-items: center; margin-top: 3px;">
            <div style="width: 10px; height: 10px; background-color: blue; border-radius: 50%; margin-right: 5px;"></div>
            <span>User Location</span>
        </div>
        <div style="display: flex; align-items: center; margin-top: 3px;">
            <div style="width: 15px; height: 3px; background-color: green; margin-right: 5px;"></div>
            <span>Parking Areas</span>
        </div>
    </div>
    '''


    # Add the legend HTML to the map
    map_obj.get_root().html.add_child(Element(legend_html))   

# Executed when website detects change in user location
def update_map(latitude, longitude):
    # Update the map with the user's location
    map_montreal = folium.Map(location=[latitude, longitude], zoom_start=16)

    # Add the blue dot to represent the user's location
    add_user_location(map_montreal, latitude, longitude)

    # Add lines to the map for each coordinate range
    for start, end in coordinate_ranges:
        add_line(map_montreal, start, end)

    # Add legend to map
    add_legend(map_montreal)

    # Save the updated map to an HTML file
    map_montreal.save(file_path)

update_map(latitude, longitude)

print("Map generated")