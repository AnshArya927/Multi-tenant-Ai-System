from flask import Flask
from .utils.database import db
from .models import *
from config import Config
from .routes import all_blueprints
from flask_jwt_extended import JWTManager

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        db.create_all()

    for bp in all_blueprints:
        app.register_blueprint(bp)

    return app
