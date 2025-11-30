# Python standard libraries
import json
import os
import sqlite3

# Third-party libs
from flask import(
    Flask,
    redirect,
    request,
    url_for
)
from flask_login import(
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user
)
from dotenv import load_dotenv
from oauthlib.oauth2 import WebApplicationClient
import requests

# Internal imports
from .db import init_db
from .user import User

# Flask app setup
def create_app():
    app = Flask(__name__)

    # Config
    load_dotenv()
    app.secret_key = os.getenv('SECRET_KEY')
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', None)
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', None)
    GOOGLE_DISCOVERY_URL = (
        'https://accounts.google.com/.well-known/openid_configuration'
    )

    # User session management setup
    login_manager = LoginManager()
    login_manager.init_app(app)

    # Naive database setup
    with app.app_context():
        try:
            init_db()
        except sqlite3.OperationalError:
            pass

    # OAuth2 client setup
    client = WebApplicationClient(GOOGLE_CLIENT_ID)

    # Flask-Login helper to retrieve a user from our db
    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    # Register blueprints
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
