from flask import Blueprint, jsonify, request
from app.models import Checkin
from app.db import db
from datetime import datetime

checkins_bp = Blueprint("checkins", __name__)

@checkins_bp.route("/checkin", methods=["POST"])
def checkin():
    data = request.get_json()
    user_id = data.get("user_id")
    meeting_id = data.get("meeting_id")
    client_id = data.get("client_id")
    notes = data.get("notes")

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    if not meeting_id:
        return jsonify({"error": "Meeting ID is required"}), 400
    if not client_id:
        return jsonify({"error": "Client ID is required"}), 400
    if not notes:
        return jsonify({"error": "Notes are required"}), 400

    new_checkin = Checkin(
        user_id=user_id,
        meeting_id=meeting_id,
        client_id=client_id,
        notes=notes
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
            "notes": new_checkin.notes
        }
    }), 201

@checkins_bp.route("/checkout/<int:checkin_id>", methods=["PUT"])
def checkout(checkin_id):
    user_id = request.json.get("user_id")
    
    checkin = Checkin.query.filter_by(id=checkin_id, user_id=user_id).first()
    if not checkin:
        return jsonify({"error": "Checkin not found"}), 404
    
    if checkin.checkout_time:
        return jsonify({"error": "Already checked out"}), 400
    
    checkin.checkout_time = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        "message": "Checked out successfully",
        "checkout_time": checkin.checkout_time.isoformat()
    }), 200

@checkins_bp.route("/all", methods=["GET"])
def get_checkins():
    user_id = request.args.get("user_id", type=int)
    
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    
    checkins = Checkin.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        "checkins": [{
            "id": checkin.id,
            "user_id": checkin.user_id,
            "meeting_id": checkin.meeting_id,
            "client_id": checkin.client_id,
            "checkin_time": checkin.checkin_time.isoformat(),
            "checkout_time": checkin.checkout_time.isoformat() if checkin.checkout_time else None,
            "notes": checkin.notes
        } for checkin in checkins]
    }), 200