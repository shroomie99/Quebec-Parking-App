from flask import Flask, render_template, request, jsonify
import folium
import os
from user_can_park_where import update_map
from flask import Flask, render_template, send_file  # Ensure send_file is imported

from pathlib import Path

# Determine the base directory of the script
base_dir = Path(__file__).parent.parent


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_location', methods=['POST'])
def get_location():
    # Get latitude and longitude from the request
    location_data = request.get_json()

    latitude = location_data.get('latitude')
    longitude = location_data.get('longitude')
    accuracy = location_data.get('accuracy')

    
    # Update the map using the received coordinates
    update_map(latitude, longitude)
    
    # Send response back to client
    print(f"Received Location: Latitude = {latitude}, Longitude = {longitude}, Accuracy = {accuracy} meters")

    return jsonify({"status": "Map updated", "latitude": latitude, "longitude": longitude})


@app.route('/display_map')
def display_map():
    # Serve the HTML file with the highlighted Montreal map
    file_path = base_dir / 'Datasets' / 'montreal_highlighted_map.html'
    return send_file(file_path)

if __name__ == '__main__':
    app.run(debug=True)
