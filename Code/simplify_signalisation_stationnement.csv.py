# update coordinates
# Reduce fields to X

import pandas as pd

from pathlib import Path

# Find the project root by navigating up from the current script's directory
project_root = Path(__file__).resolve().parents[1]  # Assumes 'Code' folder is one level deep within project

# Specify the path to your CSV file
csv_file_path = project_root / "Datasets" / "signalisation_stationnement.csv"  

# Read the CSV file into a DataFrame
data = pd.read_csv(csv_file_path, dtype={"TOPONYME_PAN": str})

# Define the columns to keep
columns_to_keep = ['POTEAU_ID_POT','POSITION_POP','PANNEAU_ID_PAN',  'DESCRIPTION_RPA', 'FLECHE_PAN', 'DESCRIPTION_REP', 'Longitude', 'Latitude']

# Select only the specified columns
data = data[columns_to_keep]


# Optionally, save the reduced DataFrame to a new CSV file
output_csv_path = project_root / "Datasets" / "simplified_signalisation_stationnement.csv"  
data.to_csv(output_csv_path, index=False)

print(f'Reduced data has been saved into a CSV')
