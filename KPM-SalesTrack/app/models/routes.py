from app.db import db
from datetime import datetime

class Route(db.Model):
    __tablename__ = 'routes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    route_date = db.Column(db.Date, nullable=False)
    total_distance_meters = db.Column(db.Integer)
    total_duration_minutes = db.Column(db.Integer)  
    encoded_polyline = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    start_location = db.Column(db.JSON)  
    end_location = db.Column(db.JSON) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)