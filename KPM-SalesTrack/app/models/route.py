from app.db import db
from datetime import datetime

class Route(db.Model):
    __tablename__ = 'routes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    route_date = db.Column(db.Date, nullable=False)
    google_route_id = db.Column(db.Integer, db.ForeignKey('google_routes.id'), nullable=False)
    route_type = db.Column(db.String(20), default='individual')
    shared_with_route_id = db.Column(db.Integer, db.ForeignKey('routes.id'))
    scheduled_departure_time = db.Column(db.DateTime)
    scheduled_return_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    