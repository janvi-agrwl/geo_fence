import uuid
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func


db = SQLAlchemy()

class User(db.Model):
    user_id = db.Column(db.String(40), primary_key=True)  # user_id is the primary key
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # hashed password
    role = db.Column(db.String(50), nullable=False)  # Can be 'employee' or 'admin'
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)


class UserToken(db.Model):
    __tablename__="user_token"
    id = db.Column(db.String(40), primary_key=True)
    user_id = db.Column(db.String(40), db.ForeignKey('user.user_id'), nullable=False)
    token = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('tokens', lazy=True))


class ProjectSite(db.Model):
    __tablename__ = 'project_sites'

    # Unique identifier for the project site
    project_id = db.Column(db.String(50), primary_key=True)
    user_id = db.Column(db.String(40), db.ForeignKey('user.user_id'), nullable=False)


    # Name of the project site
    project_name = db.Column(db.String(100), nullable=False)

    # Physical address of the project site
    address = db.Column(db.String(500), nullable=False)

    # Latitude of the center of the project site
    # Latitude with 9 digits in total and 6 decimal places
    latitude = db.Column(db.Numeric(9,6), nullable=False)

    # Longitude of the center of the project site
    longitude = db.Column(db.Numeric(9, 6), nullable=False)

    # Radius of the geo-fence around the project site (in meters)
   
    radius = db.Column(db.Numeric(6, 2), nullable=False)

    # Date when the project site was created
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)

    # Date when the project site details were last updated
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class Employee(db.Model):
    __tablename__ = 'employees'

    employee_id =db.Column(db.String(50), primary_key=True)
    
    project_id = db.Column(db.String(50), db.ForeignKey('project_sites.project_id'))
    user_id = db.Column(db.String(40), db.ForeignKey('user.user_id'), nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Encrypted password (for authentication)
    name = db.Column(db.String(200), nullable=False)  # Employee's first name
    username = db.Column(db.String(50), nullable=False,)  # Employee's last name
    email = db.Column(db.String(100), nullable=False, unique=True)  # Employee's email (should be unique)
    # Working hours fields
    work_start_time = db.Column(db.Time, nullable=False)  # Start of working hours (e.g., 9:00 AM)
    work_end_time = db.Column(db.Time, nullable=False)    # End of working hours (e.g., 5:00 PM)

class Attendance(db.Model):
    __tablename__ = 'attendance'

    attendance_id=db.Column(db.String(50), primary_key=True)
    employee_id=db.Column(db.String(50), db.ForeignKey('employees.employee_id'))
    request_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    time_interal=db.Column(db.Time, nullable=False, default=datetime.utcnow().time)
    status=db.Column(db.String(50), nullable=True)
    latitude = db.Column(db.String(512), nullable=False)  # Store encrypted latitude as a string
    longitude = db.Column(db.String(512), nullable=False)  # Store encrypted longitude as a string
    latitude_iv = db.Column(db.String(512), nullable=False)  # IV for encrypted latitude
    longitude_iv = db.Column(db.String(512), nullable=False)  # IV for encrypted longitude