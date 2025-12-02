# Python standard libraries
import sqlite3
import os

# Third-party libs
from flask import Flask
from flask_login import LoginManager
from oauthlib.oauth2 import WebApplicationClient
from dotenv import load_dotenv

# Internal imports
from .config import GOOGLE_CLIENT_ID
from .db import init_db
from .user import User

# Needed to work because google engorces HTTPS by default
load_dotenv()
insecure = os.getenv("OAUTHLIB_INSECURE_TRANSPORT")

# OAuth2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Flask app setup
def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")

    # User session management setup
    login_manager = LoginManager()
    login_manager.init_app(app)

    # Naive database setup
    with app.app_context():
        try:
            init_db()
        except sqlite3.OperationalError:
            pass

    # Flask-Login helper to retrieve a user from our db
    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    # Register blueprints
    from .auth_google import auth_google as auth_google_blueprint
    app.register_blueprint(auth_google_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
