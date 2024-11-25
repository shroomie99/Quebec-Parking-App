## Montreal Parking App Overview ##

App Name:
Montreal Parking App

Goal:
To assist users in finding free legal parking spots in Montreal based on various criteria.

Brief Description:
The app uses the user's location, the current date and time, and a customized database. To provide the user, street segments where the user can legally park their vehicle. 

How It Works:
- User accesses app/website
- User permits app to access their location
- User clicks button to "Generate Map"
- User interacts with map to find where they would like to park
   -- Green Zones: Allowed to park
   -- Red Zones: Not allowed to park

To Run App:
- setup.py : to install all dependencies
- app.py : to run application
- main.ipynb : to generate street parking data for application

Datasets required to run main.ipynb:
- Datasets\signalisation_stationnement.geojson
- Datasets\signalisation_stationnement.csv
- Datasets\gbdouble.json
- Datasets\gbdouble.csv

Required datasets are obtained here: 
1) Montreal street parking signs (Select only the "Signalisation- Stationnement" file in format CSV/geoJSON): 
https://donnees.montreal.ca/dataset/stationnement-sur-rue-signalisation-courant

2) Montreal street sides (Select only the CSV/JSON dataset):
https://donnees.montreal.ca/dataset/geobase-double



Images of Application:

1. Welcome Page
![image](https://github.com/user-attachments/assets/7e6ce3af-cdc0-46b1-9013-ebd4a1df162c)

2. Parking map Page:
![image](https://github.com/user-attachments/assets/be804da0-ff40-4480-8806-1d596c5121cd)

3. Zoom-out map of parking coverage:
![image](https://github.com/user-attachments/assets/5d846468-f45a-4acf-8c68-a08f8897a4ec)

Notes from Creator:
- I've stopped working on this project due to time limitations. Feel free to improve the code or create another Montreal Parking application with it .
- I put in a lot effort to take into account multiple factors to make the map on application be 70% reliable. Yet, my biggest issue is increasing the data realiability on the map to 90%.
- Below I've laid out suggestions to increase the data reliability to be production-ready.

Needed Improvements:
Improve data quality. By:
- In algorithm (in identify_regions_legal_to_park.py), algorithm is not cancelling signs accurately, resulting in overlapping signs. I generated code to visualize this issue but the mapping software (Folium) is generating 100MB files which is too large to open on .html.
- I have not included signs with rule_type "pannonceau" and "unknown" from sign_description_RPA_parser.py into simplified_signalisation_stationnement.csv .
- Source data limitations: Due to gbdouble.json not providing street coordinates in a directional pattern. Was forced to assume that the start coordinate on the left street, is the left corner of the street. 


