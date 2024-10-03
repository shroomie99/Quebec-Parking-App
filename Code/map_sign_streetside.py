## Should take 2 hours to run this file ##

import geopandas as gpd
from shapely.geometry import Point
import json

def load_geojson(file_path):
    return gpd.read_file(file_path)

def save_geojson(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def find_nearest_street_side(sign_point, street_sides, street_sindex):
    # Create a buffer around sign_point for an initial proximity check
    # The buffer size depends on the expected distance range of nearest streets
    buffer_size = 0.005  # Example buffer size, adjust based on your dataset.
    sign_buffer = sign_point.buffer(buffer_size)
    
    # Use spatial index to narrow down the list of potential nearest streets
    possible_matches_index = list(street_sindex.intersection(sign_buffer.bounds))
    possible_matches = street_sides.iloc[possible_matches_index]

    # Initialize nearest values
    nearest_distance = float('inf')
    nearest_id = None

    # Iterate only through the possible matches to find the truly nearest street side
    for _, street_side in possible_matches.iterrows():
        street_line = street_side.geometry
        distance = sign_point.distance(street_line)
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_id = street_side['COTE_RUE_ID']

    return nearest_id

# Load the data
street_sides_file = r'C:\Users\Benjamin\Desktop\Python Projects\Quebec Parking App\Datasets\simplified_gbdouble.json'  # Replace with your file path
signs_file = r'C:\Users\Benjamin\Desktop\Python Projects\Quebec Parking App\Datasets\simplified_signalisation_stationnement.geojson'  # Replace with your file path
output_csv_file = r'C:\Users\Benjamin\Desktop\Python Projects\Quebec Parking App\Datasets\sign_to_street_side_mapping.csv'  # Replace with your desired output path
# output_pkl_file =  r'C:\Users\Benjamin\Desktop\Python Projects\Quebec Parking App\Datasets\sign_to_street_side_mapping.pkl'  # Replace with your desired output path

street_sides = load_geojson(street_sides_file)
signs = load_geojson(signs_file)
street_sides_sindex = street_sides.sindex
print("Data loaded")

# Find the nearest street side for each parking sign. 
signs['COTE_RUE_ID'] = signs.apply(lambda sign: find_nearest_street_side(sign.geometry, street_sides, street_sides_sindex), axis=1)
print("Calculations completed")

# Drop the geometry column as it's not needed for CSV
signs = signs.drop(columns=['geometry'])

# Export the results to a new CSV file
signs.to_csv(output_csv_file, index=False)
print("Data copied into CSV file")

# signs.to_pickle('sign_street_associations.pkl')
# print("Data copied into a PKL file")

