# update coordinates
# Reduce fields to X

import pandas as pd

# Specify the path to your CSV file
csv_file_path = r'C:\Users\Benjamin\Desktop\Python Projects\Quebec Parking App\Datasets\signalisation_stationnement.csv'  # Replace with your CSV file path

# Read the CSV file into a DataFrame
data = pd.read_csv(csv_file_path, dtype={"TOPONYME_PAN": str})

# Define the columns to keep
columns_to_keep = ['POTEAU_ID_POT','POSITION_POP','PANNEAU_ID_PAN',  'DESCRIPTION_RPA', 'FLECHE_PAN', 'DESCRIPTION_REP', 'Longitude', 'Latitude']

# Select only the specified columns
data = data[columns_to_keep]

# Optionally, save the reduced DataFrame to a new CSV file
output_csv_path = r'C:\Users\Benjamin\Desktop\Python Projects\Quebec Parking App\Datasets\simplified_signalisation_stationnement.csv'  # Replace with your desired output file path
data.to_csv(output_csv_path, index=False)

print(f'Reduced data has been saved into a CSV')
