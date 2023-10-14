from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# load envs from .env file
load_dotenv()

app = Flask(__name__)
CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "127.0.0.0:5000",
                "https://viewlicense.adobe.io/*",
                "https://viewlicense.adobe.io/viewsdklicense/jwt",
            ]
        }
    },
)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SECRET_KEY"] = "N2G4Zx27gMqLX8j3ys1IcV8Q"

login_manager = LoginManager(app)
login_manager.login_view = "login"
db = SQLAlchemy(app)
