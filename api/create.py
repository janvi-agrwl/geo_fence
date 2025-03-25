

from datetime import datetime
import logging
import uuid
from flask import Blueprint, jsonify, request
from pymysql import IntegrityError

from model.models import Employee, ProjectSite
from model.models import UserToken, db,User
from werkzeug.security import generate_password_hash


create_bp=Blueprint('create', __name__)


@create_bp.route('/api/create_project_sites', methods=['POST'])
def create_project_site():
    try:
        # Get JSON data from request body
        data = request.get_json()

        # Extracting the data
        project_id=str(uuid.uuid4())
        user_id = data['user_id']
        project_name = data['project_name']
        address = data['address']
        latitude = data['latitude']
        longitude = data['longitude']
        radius = data['radius']

        # Validate required fields
        if not user_id or not project_name or not address or not latitude or not longitude or not radius:
            return jsonify({'message': 'Missing required fields'}), 400

        # Create a new ProjectSite object
        new_project_site = ProjectSite(
            project_id=project_id,
            user_id=user_id,
            project_name=project_name,
            address=address,
            latitude=latitude,
            longitude=longitude,
            radius=radius
        )

        # Add the new project site to the database
        db.session.add(new_project_site)
        db.session.commit()

        # Return a success message with the new project site details
        return jsonify({
            'message': 'Project site created successfully',
            'project_id': new_project_site.project_id
        }), 201

    except IntegrityError as e:
        db.session.rollback()  # Rollback in case of error
        return jsonify({'message': 'Integrity error, please check the data'}), 400

    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        logging.error(f"An error occurred while Project Site creation: {e}")
        logging.exception(
            "Error: Could not complete your request at the moment. Please try again later."
        )
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500
   

@create_bp.route('/api/create_employees', methods=['POST'])
def add_employee():
    try:

        data = request.get_json()

        employee_id=str(uuid.uuid4())
        user_id=str(uuid.uuid4())
        name=data['name']
        username=data['username']
        email=data['email']
        password=data['password']
        hashed_password = generate_password_hash(password)
        role="Employee"
        work_start_time=data['work_start_time']
        work_end_time=data['work_end_time']
        project_id=data['project_id']



        if not name or not username or not email or not work_start_time or not work_end_time or not password or not project_id:
            return jsonify({"message": "Missing required fields"}), 400

        # Convert strings to datetime.time objects    
        try:
            work_start_time = datetime.strptime(work_start_time, "%H:%M").time()
            work_end_time = datetime.strptime(work_end_time, "%H:%M").time()
        except ValueError:
            return jsonify({"message": "Invalid time format. Use HH:MM."}), 400
        

        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({"message": "Email is already in use"}), 400
        
        existing_user_by_username = User.query.filter_by(username=data['username']).first()
        if existing_user_by_username:
            return jsonify({"message": "Username is already in use"}), 400

        # Create User record first
        new_user = User(
            user_id=user_id,
            username=username,
            password=hashed_password,
            role="Employee",  # Default to "employee" role (or allow it to be passed in the request)
            name=name,
            email=email
        )

        # Add the new user to the session and commit
        db.session.add(new_user)
        db.session.commit()  # Commit user creation first, so user_id is available for the employee


        # Create Employee record after User creation
        new_employee = Employee(
            employee_id=employee_id,
            project_id=project_id,
            user_id=user_id,  # This ties the employee to the user
            password=hashed_password,  # Ensure the employee password is hashed as well
            name=name,
            username=username,
            email=email,
            work_start_time=work_start_time,
            work_end_time=work_end_time
        )

        # Add the new employee to the session and commit
        db.session.add(new_employee)
        db.session.commit()
 
        return jsonify({
                "message": "Employee and user created successfully",
                "employee_id": new_employee.employee_id,
                "user_id": new_user.user_id
        }), 201
    
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        logging.error(f"An error occurred while Project Site creation: {e}")
        logging.exception(
            "Error: Could not complete your request at the moment. Please try again later."
        )
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500
   