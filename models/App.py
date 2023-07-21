from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy

# load envs from .env file
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL") 
app.config['SECRET_KEY'] = 'N2G4Zx27gMqLX8j3ys1IcV8Q'

login_manager = LoginManager(app)
login_manager.login_view = 'login'
db = SQLAlchemy(app)

