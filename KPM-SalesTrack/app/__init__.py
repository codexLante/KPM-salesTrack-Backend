from flask import Flask
from .config import Config
from .db import db,migrate
from app.routes import users_bp, meetings_bp
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt

bcrypt=Bcrypt()
jwt=JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)


    # Initialize db
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(meetings_bp, url_prefix="/meetings")

    return app
