from flask import Blueprint, jsonify, request
from app.models import Checkin, Meeting
from app.db import db
from datetime import datetime
from geopy.distance import geodesic
from flask_jwt_extended import get_jwt_identity, get_jwt
from app.utils import reverse_geocode, role_required

checkins_bp = Blueprint("checkins", __name__)


@checkins_bp.route("/checkin", methods=["POST"])
@role_required('sales')
def checkin():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        meeting_id = data.get("meeting_id")
        client_id = data.get("client_id")
        user_location = data.get("location")

        if not all([user_id, meeting_id, client_id, user_location]):
            return jsonify({"error": "All fields including location are required"}), 400
        
        current_user_id = int(get_jwt_identity())
        role = get_jwt().get("role")

        if role != "admin" and current_user_id != user_id:
            return jsonify({"error": "Access denied. You can only check in for yourself."}), 400

        meeting = Meeting.query.get(meeting_id)
        if not meeting or not meeting.location:
            return jsonify({"error": "Meeting location not found"}), 404

        meeting_coords = (meeting.location["coordinates"][1], meeting.location["coordinates"][0])
        user_coords = (user_location["lat"], user_location["lon"])

        distance = geodesic(user_coords, meeting_coords).meters
        if distance > 50:
            return jsonify({
                "error": f"Too far from meeting location ({int(distance)}m). Must be within 50m."
            }), 400

        geocoded_location = reverse_geocode(user_location["lat"], user_location["lon"])
        if not geocoded_location:
            return jsonify({"error": "Could not reverse geocode your location"}), 400
        
        new_checkin = Checkin(
            user_id=user_id,
            meeting_id=meeting_id,
            client_id=client_id,
            location=geocoded_location
        )

        db.session.add(new_checkin)
        db.session.commit()

        return jsonify({
            "message": "Checked in successfully",
            "checkin": {
                "id": new_checkin.id,
                "user_id": new_checkin.user_id,
                "meeting_id": new_checkin.meeting_id,
                "client_id": new_checkin.client_id,
                "checkin_time": new_checkin.checkin_time.isoformat(),
                "location": new_checkin.location
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to check in: {str(e)}"}), 500