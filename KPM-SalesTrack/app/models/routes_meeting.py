from app.db import db
from datetime import datetime

class RouteMeeting(db.model):
  __tablename__ = 'routes_meetings'

  id = db.Column(db.Integer, primary_key=True)
  route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
  meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id'), nullable=False)
  stop_order = db.Column(db.Integer, nullable=False)
  estimated_arrival_time = db.Column(db.DateTime)
  estimated_departure_time = db.Column(db.DateTime)
  actual_arrival_time = db.Column(db.Integer)
  actual_departure_time = db.column(db.Integer)
  status = db.column(db.String(20), default='scheduled')
  notes = db.column(db.Text)