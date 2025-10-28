from app.db import db
from datetime import datetime


class Checkin(db.Model):
    __tablename__ = 'checkins'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id'), nullable=False) 
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)  
    location = db.Column(db.JSON, nullable=True)
    checkin_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    checkout_time = db.Column(db.DateTime)