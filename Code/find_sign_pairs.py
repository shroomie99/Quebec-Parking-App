""" Determine each sign's boundaries on a streetside. And append data to combine_dataset.py ###

For each sign_id, identify each signs pair. And append to combine_datasets.CSV 
English Inputs: streetside_ID + sign id + sign coordinate + sign direction on streetside + boundary coordinate (paired sign or street boundary)
"""

import pandas as pd
import json
import time

# Load sample_user_input
combined_datasets_csv_path = r'C:\Users\Benjamin\Desktop\Python Projects\Quebec Parking App\Datasets\combined_datasets.csv'

# Load the data from CSV files into DataFrames
combined_datasets = pd.read_csv(combined_datasets_csv_path)

# Function to find the effective area where the sign rules applies
def find_effective_area(df):
    results = []

    for index, row in df.iterrows():

        # Columns used in CSV
        panneau_id = row['PANNEAU_ID_PAN']
        fleche = row['FLECHE_PAN']
        cote_rue_id = row['COTE_RUE_ID']
        description_rpa = row['DESCRIPTION_RPA']
        sign_longitude = row['sign_longitude']
        sign_latitude = row['sign_latitude']
        street_side_coordinate1_lon = row['street_side_coordinate1_lon']
        street_side_coordinate1_lat = row['street_side_coordinate1_lat']
        street_side_coordinate2_lon = row['street_side_coordinate2_lon']
        street_side_coordinate2_lat = row['street_side_coordinate2_lat']
        
        sign_effective_area_coordinate1 = (sign_longitude, sign_latitude)
        sign_effective_area_coordinate2 = None

        # When sign points to right side of streetside
        if fleche == 2:
            # Find row with COTE_RUE_ID and DESCRIPTION_RPA matching and FLECHE_PAN == 3
            matching_row = df[(df['COTE_RUE_ID'] == cote_rue_id) & 
                              (df['DESCRIPTION_RPA'] == description_rpa) & 
                              (df['FLECHE_PAN'] == 3)]
            
            # Found a sign pair. Match with sign pair
            if not matching_row.empty:
                matched_row = matching_row.iloc[0]
                sign_effective_area_coordinate2 = (matched_row['sign_longitude'], matched_row['sign_latitude'])

            # Not Found a sign pair. Match with last streetedge
            else:
                sign_effective_area_coordinate2 = (street_side_coordinate2_lon, street_side_coordinate2_lat)
        
        # When sign points to left side of streetside
        elif fleche == 3:
            # Find row with COTE_RUE_ID and DESCRIPTION_RPA matching and FLECHE_PAN == 2
            matching_row = df[(df['COTE_RUE_ID'] == cote_rue_id) & 
                              (df['DESCRIPTION_RPA'] == description_rpa) & 
                              (df['FLECHE_PAN'] == 2)]
            
            # Found a sign pair. Match with sign pair
            if not matching_row.empty:
                matched_row = matching_row.iloc[0]
                sign_effective_area_coordinate2 = (matched_row['sign_longitude'], matched_row['sign_latitude'])

            # Not Found a sign pair. Match with first streetedge
            else:
                sign_effective_area_coordinate2 = (street_side_coordinate1_lon, street_side_coordinate1_lat)

        # Set effective area as the whole streetside. 
        else:
            sign_effective_area_coordinate1 = (street_side_coordinate1_lon, street_side_coordinate1_lat)
            sign_effective_area_coordinate2 = (street_side_coordinate2_lon, street_side_coordinate2_lat)
 

        # Output
        results.append({
            'PANNEAU_ID_PAN': panneau_id,
            'sign_effective_area_coordinate1': sign_effective_area_coordinate1,
            'sign_effective_area_coordinate2': sign_effective_area_coordinate2
        })
    return pd.DataFrame(results)

# Find effective area coordinates
effective_area_df = find_effective_area(combined_datasets)

###  Append outputs to CSV
# Merge the new effective area coordinates with the original dataset
combined_with_effective_area = combined_datasets.merge(effective_area_df, on='PANNEAU_ID_PAN', how='left')

# Save the combined dataset with effective area coordinates to the same CSV file
combined_with_effective_area.to_csv(combined_datasets_csv_path, index=False)

print("Updated combined_datasets.csv with sign pairs")


"""

## Blueprint for the above code
#     Find coordinate pair:
#         For each sign id {PANNEAU_ID_PAN}, 
#             If sign direction {FLECHE_PAN} is 2:
#                 Find another sign/{row} that has {COTE_RUE_ID} is equal to original.{COTE_RUE_ID} && {DESCRIPTION_RPA} is equal to original.{DESCRIPTION_RPA} && sign direction {FLECHE_PAN} is 3.  
#                     If Found, set its sign coordinates to paired boundary.
#                         [sign_effective_area_coordinate1 = original row {sign_longitude}, {sign_latitude}; sign_effective_area_coordinate2 = new row ({sign_longitude}, {sign_latitude})
#                     If cannot find. 
#                         Set paired boundary as the last street_side_coordinate 
#                             [sign_effective_area_coordinate1 = {sign_longitude}, {sign_latitude}; sign_effective_area_coordinate2 = {street_side_coordinate2_lon, street_side_coordinate2_lat}]


#             If sign direction {FLECHE_PAN} is 3:
#                     Find another sign/{row} that has {COTE_RUE_ID} is equal to original.{COTE_RUE_ID} && {DESCRIPTION_RPA} is equal to original.{DESCRIPTION_RPA} && sign direction {FLECHE_PAN} is 2.  
#                         If Found, set its sign coordinates to paired boundary.
#                         If cannot find. 
#                             Set paired boundary as the first street_side_coordinate 
#                                 [sign_effective_area_coordinate1 = {sign_longitude}, {sign_latitude}; sign_effective_area_coordinate2 = {street_side_coordinate1_lon, street_side_coordinate1_lat}]

#             Else,
#                 Set paired boundary as first and last street side coordinate
#                 [sign_effective_area_coordinate1 = {street_side_coordinate1_lon, street_side_coordinate1_lat}; sign_effective_area_coordinate2 = {street_side_coordinate2_lon, street_side_coordinate2_lat}]


# Output: Sign id {PANNEAU_ID_PAN}, region sign rules applies to [{sign_effective_area_coordinate1}, {sign_effective_area_coordinate2}]


# Then, using combine_datasets.CSV dataset:
# - Using sign id {PANNEAU_ID_PAN}. Append the variable, region sign rules applies to, [{sign_effective_area_coordinate1}, {sign_effective_area_coordinate2}].
# ################################
"""