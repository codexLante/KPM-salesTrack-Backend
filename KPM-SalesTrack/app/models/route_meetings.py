from app.db import db
from datetime import datetime

class RouteMeeting(db.Model):
    __tablename__ = 'route_meetings'

    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id'), nullable=False)
    stop_order = db.Column(db.Integer, nullable=False)
    stop_type = db.Column(db.String(20), default='meeting')
    estimated_arrival_time = db.Column(db.DateTime, nullable=False)
    estimated_departure_time = db.Column(db.DateTime, nullable=False)
    distance_from_previous_meters = db.Column(db.Integer)
    duration_from_previous_seconds = db.Column(db.Integer) 
    status = db.Column(db.String(20), default='scheduled')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    