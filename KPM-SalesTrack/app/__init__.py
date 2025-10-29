from flask import Flask
from .config import Config
from .db import db,migrate
from app.routes import users_bp, meetings_bp, clients_bp
from flask_jwt_extended import JWTManager
from app.routes import users_bp,tasks_bp,checkins_bp,objectives_bp
from flask_bcrypt import Bcrypt

bcrypt=Bcrypt()
jwt=JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)


    # Initialize db
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(meetings_bp, url_prefix="/meetings")
    app.register_blueprint(tasks_bp, url_prefix="/tasks")
    app.register_blueprint(checkins_bp, url_prefix="/checkins")
    app.register_blueprint(clients_bp, url_prefix="/clients")
    app.register_blueprint(objectives_bp, url_prefix="/objectives")

    return app
