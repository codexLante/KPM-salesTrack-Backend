from flask import Blueprint,jsonify,request,send_from_directory
from app.models import Meeting
from app.db import db
from datetime import datetime


meetings_bp = Blueprint("meetings", __name__)

@meetings_bp.route("/create", methods=["POST"])
def create_meeting():
    data = request.get_json()

    user_id = data.get("user_id")
    client_id = data.get("client_id")
    title = data.get("title")
    duration = data.get("duration")
    location = data.get("location")
    meeting_type = data.get("meeting_type")
    scheduled_time = data.get("scheduled_time")
    scheduled_date = data.get("scheduled_date")

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    if not client_id:
        return jsonify({"error": "Client ID is required"}), 400
    if not title:
        return jsonify({"error": "Title is required"}), 400
    if not duration:
        return jsonify({"error": "Duration is required"}), 400
    if not location:
        return jsonify({"error": "Location is required"}), 400
    if not meeting_type:
        return jsonify({"error": "Meeting type is required"}), 400
    if not scheduled_date:
        return jsonify({"error": "Scheduled date is required"}), 400
    if not scheduled_time:
        return jsonify({"error": "Scheduled time is required"}), 400

    
    if not isinstance(duration, int) or duration <= 0:
        return jsonify({"error": "Duration must be an integer"}), 400

    if not isinstance(scheduled_time, str) or not isinstance(scheduled_date, str):
        return jsonify({"error": "Scheduled time and date must be strings"}), 400

    try:
        scheduled_time = datetime.fromisoformat(scheduled_time)
        scheduled_date = datetime.fromisoformat(scheduled_date).date()
    except ValueError:
        return jsonify({"error": "Invalid date or time format"}), 400

    new_meeting = Meeting(
        user_id=user_id,
        client_id=client_id,
        title=title,
        duration=duration,
        location=location,
        meeting_type=meeting_type,
        scheduled_time=scheduled_time,
        scheduled_date=scheduled_date
    )

    db.session.add(new_meeting)
    db.session.commit()

    return jsonify({
        "message": "Meeting created successfully",
        "meeting": {
            "id": new_meeting.id,
            "user_id": new_meeting.user_id,
            "client_id": new_meeting.client_id,
            "title": new_meeting.title,
            "duration": new_meeting.duration,
            "location": new_meeting.location,
            "meeting_type": new_meeting.meeting_type,
            "scheduled_time": new_meeting.scheduled_time.isoformat(),
            "scheduled_date": new_meeting.scheduled_date.isoformat(),
            "created_at": new_meeting.created_at.isoformat() if new_meeting.created_at else None
        }
    }), 201

@meetings_bp.route("/get_meeting", methods=["GET"])
def get_meeting(meeting_id):
    meeting = Meeting.query.get(meeting_id)

    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404

    return jsonify({
        "id": meeting.id,
        "user_id": meeting.user_id,
        "client_id": meeting.client_id,
        "title": meeting.title,
        "duration": meeting.duration,
        "location": meeting.location,
        "meeting_type": meeting.meeting_type,
        "scheduled_time": meeting.scheduled_time.isoformat(),
        "scheduled_date": meeting.scheduled_date.isoformat(),
        "created_at": meeting.created_at.isoformat() if meeting.created_at else None
    }), 200

@meetings_bp.route("/Update", methods=["PUT"])
def update_meeting(meeting_id):
    data = request.get_json()
    meeting = Meeting.query.get(meeting_id)

    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404

    user_id = data.get("user_id", meeting.user_id)
    client_id = data.get("client_id", meeting.client_id)
    title = data.get("title", meeting.title)
    duration = data.get("duration", meeting.duration)
    location = data.get("location", meeting.location)
    meeting_type = data.get("meeting_type", meeting.meeting_type)
    scheduled_time = data.get("scheduled_time", meeting.scheduled_time.isoformat())
    scheduled_date = data.get("scheduled_date", meeting.scheduled_date.isoformat())

    if not isinstance(duration, int) or duration <= 0:
        return jsonify({"error": "Duration must be a positive integer"}), 400

    try:
        scheduled_time = datetime.fromisoformat(scheduled_time)
        scheduled_date = datetime.fromisoformat(scheduled_date).date()
    except ValueError:
        return jsonify({"error": "Invalid date or time format"}), 400

    meeting.user_id = user_id
    meeting.client_id = client_id
    meeting.title = title
    meeting.duration = duration
    meeting.location = location
    meeting.meeting_type = meeting_type
    meeting.scheduled_time = scheduled_time
    meeting.scheduled_date = scheduled_date

    db.session.commit()

    return jsonify({
        "message": "Meeting updated successfully",
        "meeting": {
            "id": meeting.id,
            "user_id": meeting.user_id,
            "client_id": meeting.client_id,
            "title": meeting.title,
            "duration": meeting.duration,
            "location": meeting.location,
            "meeting_type": meeting.meeting_type,
            "scheduled_time": meeting.scheduled_time.isoformat(),
            "scheduled_date": meeting.scheduled_date.isoformat(),
            "created_at": meeting.created_at.isoformat() if meeting.created_at else None
        }
    }), 201

@meetings_bp.route("/delete", methods=["DELETE"])
def delete_meeting(meeting_id):
    meeting = Meeting.query.get(meeting_id)

    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404

    db.session.delete(meeting)
    db.session.commit()

    return jsonify({
        "message": "Meeting deleted successfully"
    }), 200