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