from app.db import db
from datetime import datetime, timezone

class User(db.Model):
    __tablename__ = 'users'

    ROLE_ADMIN = 'admin'
    ROLE_SALESMAN = 'salesman'
    VALID_ROLES = [ROLE_ADMIN, ROLE_SALESMAN]

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
