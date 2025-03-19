from flask import Flask
import secrets

from flask_cors import CORS
from config import Config 
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from model.models import db
from api.auth import auth_bp
from api.location import location_bp
# Create a Flask application
import pymysql
app = Flask(__name__)


CORS(app)

# Load the configuration from the Config class in config.py
app.config.from_object(Config)  # This loads all configurations from the Config class

db.init_app(app) 
migrate = Migrate(app, db)
jwt = JWTManager(app)



# Define a route for the root URL
@app.route('/')
def hello_world():
    return "Hello, World!"


#THIS HELPS GENERATE A LONG RANDOM SECRET KEY 
"""secret_key = secrets.token_hex(32)
print(secret_key)"""

app.register_blueprint(auth_bp)
app.register_blueprint(location_bp)

# Run the application
if __name__ == '__main__':
    app.run(debug=True,port=5004)


