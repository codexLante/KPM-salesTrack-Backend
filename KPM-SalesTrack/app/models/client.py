from app.db import db
from datetime import datetime, timezone

class Client(db.Model):
    __tablename__ = 'clients'

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), nullable=False)
    location = db.Column(db.JSON, nullable=False)  
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    