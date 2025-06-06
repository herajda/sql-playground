# Initializes the Flask app

import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv


def create_app():
    # Load variables from a .env file if present so environment configuration
    # such as ADMIN_PASSWORD can be provided without setting system-wide
    # variables.
    load_dotenv()

    app = Flask(__name__)
    CORS(app)
        # Serve the Single-Page App
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def spa(path):
        file_path = os.path.join(app.static_folder, path)
        if path and os.path.exists(file_path):
            return send_from_directory(app.static_folder, path)
        # anything else → index.html, so the Svelte router can take over
        return send_from_directory(app.static_folder, "index.html")

    from .routes import main
    app.register_blueprint(main)

    return app


