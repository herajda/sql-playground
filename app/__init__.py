# Initializes the Flask app

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv


def create_app():
    # Load variables from a .env file if present so environment configuration
    # such as ADMIN_PASSWORD can be provided without setting system-wide
    # variables.
    load_dotenv()

    app = Flask(__name__)
    CORS(app)

    from .routes import main
    app.register_blueprint(main)

    return app


