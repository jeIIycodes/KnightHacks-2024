# app.py

from flask import Flask
from AiPredictor.config import Config
from blueprints.routes import database_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints
    app.register_blueprint(database_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=8000, debug=True)
