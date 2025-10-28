from app.db import db
from datetime import datetime

class RouteSegment(db.Model):
  __tablename__ = 'routes_segments'

  id = db.Column(db.Integer, primary_key=True)
  route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
  segment_order = db.Column(db.Integer, nullable=False)
  distance_meters = db.Column(db.Integer)
  duration_seconds = db.Column(db.Integer)
  segment_polyline = db.Column(db.Text)

  