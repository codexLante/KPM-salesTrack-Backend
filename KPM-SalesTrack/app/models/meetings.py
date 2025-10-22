from app.db import db
from datetime import datetime, timezone

class Meeting(db.Model):
    __tablename__ = 'meetings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    # user = db.relationship('User', backref=db.backref('meetings', lazy=True))
    # client = db.relationship('Client', backref=db.backref('meetings', lazy=True))
    title = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    location = db.Column(db.JSON, nullable=False)  # Location can be a string or JSON object
    meeting_type = db.Column(db.String(50), nullable=False)  
    scheduled_time = db.Column(db.DateTime, nullable=False)  # Scheduled time for the meeting
    scheduled_date = db.Column(db.Date, nullable=False)  # Scheduled date for the meeting