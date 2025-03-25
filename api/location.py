from datetime import datetime
import logging
import os
import uuid
from dotenv import load_dotenv
from flask import Blueprint, jsonify, request
from geopy.distance import geodesic
from model.models import Employee, ProjectSite, db
from model.models import Attendance
from api.aes import decrypt_value, encrypt_value
import pytz

location_bp = Blueprint('location', __name__)

load_dotenv()


def compare_location(employee_id,lattitude,latitude_iv,longitude,longitude_iv):
    # Get the latitude and longitude from the request
    """  data = request.get_json()
    latitude = data.get('latitude')     #north/south#comes first
    longitude = data.get('longitude')   #east/west #second position"""
    employee_information=db.session.query(Employee).filter(Employee.employee_id==employee_id).first()
    fetched_project_id=employee_information.project_id
    project_info=db.session.query(ProjectSite).filter(ProjectSite.project_id==fetched_project_id).first()
   

    decipher_lattitude=decrypt_value(lattitude,latitude_iv,aes_key)
    
    decipher_longitude=decrypt_value(longitude,longitude_iv,aes_key)
    current_coordinates=(decipher_lattitude,decipher_longitude)
    project_coordinates=(project_info.latitude, project_info.longitude)

    radius=project_info.radius
    print(radius)
    distance = geodesic(current_coordinates, project_coordinates).meters
    print(distance)
    #as the radius stored is in meters we find the distance in meter
    if distance<=radius:
        status="present"
    
    else:
        status="absent"
    return status
    


#as the key is in hexadecimal 
key=os.getenv('AES_KEY')
#we convert to byte string
def convert_hex_to_byte(key):
    # Convert hex string to an integer
    integer_value = int(key, 16)
    #16 represents hexadecimal number

    
    byte_string = integer_value.to_bytes((integer_value.bit_length() + 7) // 8, byteorder='big')
    return byte_string

aes_key=convert_hex_to_byte(key=key)

"""lattitude=22.3104

cipher,iv=encrypt_value(lattitude,aes_key)
print("cipher",cipher)
print("iv",iv)

decipher=decrypt_value(cipher,iv,aes_key)
print(decipher)
"""
@location_bp.route("/api/track_attendance", methods=['POST'])
def request_location():
    try:
        data = request.get_json()
        employee_id = data['employee_id']
        latitude = data['lattitude']
        longitude = data['longitude']
        
        current_time_utc = datetime.utcnow()
        ist = pytz.timezone('Asia/Kolkata')
        current_time_ist = current_time_utc.replace(tzinfo=pytz.utc).astimezone(ist)
        current_date_ist = current_time_ist.date()
        current_time=current_time_ist.time()

        employee_info=db.session.query(Employee).filter(Employee.employee_id==employee_id).first()

        if not employee_info:
            logging.error(f"Employee with ID {employee_id} not found.")
            return jsonify({"message": "Employee not found."}), 404
        print(current_time)
        print(employee_info.work_start_time)
        print(current_time<employee_info.work_start_time)
        if employee_info.work_start_time <= current_time <= employee_info.work_end_time:

            if not employee_id or not latitude or not longitude :
                return jsonify({"message": "Missing required fields"}), 400
            
            encrypted_latitude,latitude_iv=encrypt_value(latitude,aes_key)
            encrypted_longitude,longitude_iv=encrypt_value(longitude,aes_key)
            
            status=compare_location(employee_id=employee_id,lattitude=encrypted_latitude,latitude_iv=latitude_iv,longitude=encrypted_longitude,longitude_iv=longitude_iv)
            attendance_id=str(uuid.uuid4())
            new_record=Attendance(attendance_id=attendance_id,
                                employee_id=employee_id,
                                latitude=encrypted_latitude,
                                longitude=encrypted_longitude,
                                latitude_iv=latitude_iv,
                                longitude_iv=longitude_iv,
                                status=status,
                                request_date=current_date_ist,
                                time_interal=current_time
                                )

            db.session.add(new_record)
            db.session.commit()
            logging.info(f"Attendance recorded for employee ID {employee_id}.")
            return jsonify({"message":"Attendance Recorded"}),201
        
        else:
            logging.warning(f"Attempted to record attendance outside of working hours for employee {employee_id}.")
            return jsonify({"message":"Gathering location is unavailable outside of working hours."}),200

    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"message": "An unexpected error occurred. Please try again later."}), 500

