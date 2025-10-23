from app.db import db
from datetime import datetime

class Meeting(db.Model):
    __tablename__ = 'meetings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    location = db.Column(db.JSON, nullable=False)  
    meeting_type = db.Column(db.String(50), nullable=False)  
    scheduled_time = db.Column(db.DateTime, nullable=False) 
    scheduled_date = db.Column(db.Date, nullable=False) 