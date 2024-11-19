import pandas as pd
import json

from pathlib import Path

# Find the project root by navigating up from the current script's directory
project_root = Path(__file__).resolve().parents[1]  # Assumes 'Code' folder is one level deep within project

# Load the JSON file
json_file_path = project_root / "Datasets" / "simplified_signalisation_stationnement.json"  
with open(json_file_path, 'r') as file:
    json_data = json.load(file)

# Extract features from JSON
features = json_data['features']

# Create a DataFrame for the features with the PANNEAU_ID_PAN and coordinates
json_df = pd.DataFrame({
    'PANNEAU_ID_PAN': [feature['properties']['PANNEAU_ID_PAN'] for feature in features],
    'Longitude': [feature['geometry']['coordinates'][0] for feature in features],
    'Latitude': [feature['geometry']['coordinates'][1] for feature in features]
})

# Specify the path to your CSV file
csv_file_path = project_root / "Datasets" / "simplified_signalisation_stationnement.csv"  

# Read the CSV file into a DataFrame
csv_data = pd.read_csv(csv_file_path)

# Merge the CSV data with the JSON data based on PANNEAU_ID_PAN
updated_csv_data = pd.merge(csv_data, json_df, on='PANNEAU_ID_PAN', how='left')

# To overwrite the original Longitude and Latitude with the new values
updated_csv_data['Longitude'] = updated_csv_data['Longitude_y']
updated_csv_data['Latitude'] = updated_csv_data['Latitude_y']

# Drop the redundant columns from the merge
updated_csv_data.drop(columns=['Longitude_x', 'Latitude_x', 'Longitude_y', 'Latitude_y'], inplace=True)

# Export the updated DataFrame to a new CSV file
updated_csv_path = project_root / "Datasets" / "simplified_signalisation_stationnement.csv"  
updated_csv_data.to_csv(updated_csv_path, index=False)

print(f'Coordinates updated in CSV, simplified_signalisation_stationnement.csv')
