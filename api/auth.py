from datetime import timedelta
import datetime
import os
from flask import Blueprint, jsonify, request
import uuid
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
import jwt
from sqlalchemy import and_
from werkzeug.security import generate_password_hash,check_password_hash
from model.models import UserToken, db,User
import logging

auth_bp = Blueprint('auth', __name__)

access_token_expiry_time=timedelta(hours=1)
refresh_token_expiry_time=timedelta(days=7)

ACCESS_TOKEN_SECRET=os.getenv('ACCESS_TOKEN_SECRET')
REFRESH_TOKEN_SECRET=os.getenv('REFRESH_TOKEN_SECRET')


def create_access_token(user_id):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)  # Access token expires in 15 minutes
    return jwt.encode({'user_id': user_id, 'exp': expiration}, ACCESS_TOKEN_SECRET, algorithm='HS256')


def create_refresh_token(user_id):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(days=7)  # Refresh token expires in 7 days
    return jwt.encode({'user_id': user_id, 'exp': expiration}, REFRESH_TOKEN_SECRET, algorithm='HS256')


def is_valid_email(email):
    import re
    return re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email)



def decode_jwt(jwt_token):
    decoded = jwt.decode(jwt_token, options={"verify_signature": False})
    return decoded

@auth_bp.route('/api/login', methods=['POST'])
def signin():
    try:
        data = request.get_json()
        identifier = data.get('identifier')
        password = data.get('password')
        
        user = User.query.filter((User.email == identifier) | (User.username == identifier)).first()
        
        if not user or not check_password_hash(user.password, password):
            return jsonify({'message': 'Invalid credentials!'}), 401
        
        
        access_token= create_access_token(user_id=user.user_id)
        decoded_payload = decode_jwt(access_token)
        print("Decoded Payload:", decoded_payload)
        refresh_token=create_refresh_token(user_id=user.user_id)
        decoded_payload = decode_jwt(access_token)
        print(decoded_payload['user_id'])
        print("Decoded Payload:", decoded_payload)

        id=uuid.uuid4()
        token = UserToken(id=id,user_id=user.user_id, token=refresh_token)
        db.session.add(token)
        db.session.commit()
        logging.info("Logging successful")
        return jsonify({
            'message': 'Login successful!',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_id':user.user_id
        }), 200
        
    except Exception as e:
        logging.error(f"Encountering an error when trying to login: {e}")
        logging.exception("Error: Could not log in to your account. Please try again later.")
        return jsonify({'message': 'An error occurred!', 'error': str(e)}), 500
    

@auth_bp.route("/api/refresh",methods=['GET','POST'])
def refresh():
    try:
        data= request.get_json()
        refresh_token = data.get('refresh_token')

        if not refresh_token:
            return jsonify({'message': 'Refresh token is required!'}), 400
        
        payload=decode_jwt(refresh_token)
        
        user_id=payload['user_id']

        print(refresh_token,user_id)    
        stored_token = db.session.query(UserToken).filter(and_(UserToken.token==refresh_token,UserToken.user_id==user_id)).first()
        print(stored_token)
        if not stored_token:
            return jsonify({'message': 'Invalid refresh token!'}), 401
        
        db.session.delete(stored_token)
        

        new_access_token= create_access_token(user_id=stored_token.user_id)
        new_refresh_token=create_refresh_token(user_id=stored_token.user_id)


        id=uuid.uuid4()
        new_token = UserToken(id=id, user_id=user_id, token=new_refresh_token)
        db.session.add(new_token)
        db.session.commit()
        
        
        return jsonify({
            'message': 'Token refreshed successfully!',
            'access_token': new_access_token,
            'refresh_token': new_refresh_token
        }), 200

    except Exception as e :
        return jsonify({"message":"error occured", 'error': str(e)}),500
    


@auth_bp.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    try:

        if 'Authorization' in request.headers:

            token=request.headers.get('Authorization')
            print (token)
            return "okay"
            
            token = request.headers['Authorization'].split(" ")[1]  # Assuming format 'Bearer <token>'
            print(token)
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        
        try:
            # Decode the token to get the user_id
            decoded_token = jwt.decode(token, ACCESS_TOKEN_SECRET, algorithms=["HS256"])
            print(decoded_token)
            current_user_id = decoded_token['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 403
        
        data = request.get_json()
        refresh_token = data.get('refresh_token')


        if not refresh_token:
            return jsonify({'message': 'Refresh token is required!'}), 400
        
        payload=decode_jwt(refresh_token)
        
        user_id=payload['user_id']


        


        stored_token = db.session.query(UserToken).filter(and_(UserToken.token==refresh_token,UserToken.user_id==current_user_id)).first()

        
        if stored_token:
            db.session.delete(stored_token)
            db.session.commit()

        return jsonify({'message': 'Logout successful!'}), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred!', 'error': str(e)}), 500


@auth_bp.route("/api/get_token_from_header")
def get_token():
    if 'Authorization' in request.headers:
            
        token=request.headers.get('Authorization')
        print (token)
        return "okay"
    else:
        return "not okay"