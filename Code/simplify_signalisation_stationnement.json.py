import json

from pathlib import Path

# Find the project root by navigating up from the current script's directory
project_root = Path(__file__).resolve().parents[1]  # Assumes 'Code' folder is one level deep within project

# Load the GeoJSON file
input_file_path = project_root / "Datasets" / "signalisation_stationnement.json"  
with open(input_file_path, 'r') as file:
    data = json.load(file)

# Process each feature to keep only the first and last coordinates
for feature in data['features']:
    if feature['geometry']['type'] == 'LineString':
        coords = feature['geometry']['coordinates']
        if len(coords) > 1:
            # Keep only the first and last coordinates
            feature['geometry']['coordinates'] = [coords[0], coords[-1]]

    # Modify each feature's properties to only retain "COTE_RUE_ID"
    PANNEAU_ID_PAN = feature['properties'].get('PANNEAU_ID_PAN')
    feature['properties'] = {'PANNEAU_ID_PAN': PANNEAU_ID_PAN}


# Save the modified data to a new GeoJSON file
output_file_path = project_root / "Datasets" / "simplified_signalisation_stationnement.json"  
with open(output_file_path, 'w') as file:
    json.dump(data, file, indent=4)

print(f'Reduced data has been saved into a CSV')
