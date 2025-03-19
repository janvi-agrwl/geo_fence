from flask import Blueprint, jsonify, request
from geopy.distance import geodesic


location_bp = Blueprint('location', __name__)


@location_bp.route('/compare_location', methods=['POST'])
def compare_location():
    # Get the latitude and longitude from the request
    data = request.get_json()
    latitude = data.get('latitude')     #north/south#comes first
    longitude = data.get('longitude')   #east/west #second postion
    current_coordinates=(latitude,longitude)
    coord2=(22.3104 , 73.1813 )

    
    distance = geodesic(current_coordinates, coord2).kilometers
    round_distance=round(distance,2)
    
    

    if latitude and longitude:
        return jsonify({ 
            "round_distance":round_distance,
            'distance between the current coordinates and the hardcoded coordinates is ': distance,
            'latitude': latitude,
            'longitude': longitude,
            'message': 'Location received successfully!'})
    else:
        return jsonify({'message': 'Latitude and Longitude are required!'}), 400



