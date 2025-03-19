import uuid
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash

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


