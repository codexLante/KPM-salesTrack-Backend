from app.db import db
from datetime import datetime

class GoogleRoute(db.Model):


    __tablename__ = 'google_routes'
    
    id = db.Column(db.Integer, primary_key=True)
    raw_response = db.Column(db.JSON, nullable=False)
    total_distance_meters = db.Column(db.Integer)
    total_duration_seconds = db.Column(db.Integer)
    encoded_polyline = db.Column(db.Text)
    waypoints_hash = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
