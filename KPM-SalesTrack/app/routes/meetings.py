from flask import Blueprint, jsonify, request
from app.models import Meeting, User, Client
from app.db import db
from datetime import datetime
from app.utils import geocode_address
from flask_jwt_extended import get_jwt_identity, get_jwt
from app.utils import admin_required, sales_or_admin_required,owner_or_admin_required

meetings_bp = Blueprint("meetings", __name__)
@meetings_bp.route("/admin/all", methods=["GET"])
@admin_required
def admin_get_all_meetings():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status_filter = request.args.get('status', 'all')
    user_id = request.args.get('user_id', type=int)
    
    if page < 1 or per_page < 1 or per_page > 100:
        return jsonify({"error": "Invalid pagination parameters"}), 400

    try:
        query = Meeting.query
        
        if status_filter and status_filter.lower() != 'all':
            if status_filter.lower() == 'upcoming':
                query = query.filter(Meeting.scheduled_date >= datetime.now().date())
            elif status_filter.lower() == 'completed':
                query = query.filter(Meeting.scheduled_date < datetime.now().date())
        
        if user_id:
            query = query.filter(Meeting.user_id == user_id)
        
        pagination = query.order_by(Meeting.scheduled_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        meetings_list = []
        for m in pagination.items:
            client = Client.query.get(m.client_id)
            user = User.query.get(m.user_id)
            
            meetings_list.append({
                "id": m.id,
                "client": client.company_name if client else "Unknown",
                "contactPerson": client.contact_person if client else "N/A",
                "meetingType": m.meeting_type,
                "date": m.scheduled_date.isoformat(),
                "time": m.scheduled_time.strftime('%H:%M'),
                "location": m.location.get("label") if m.location else m.location,
                "status": "Completed" if m.scheduled_date < datetime.now().date() else "Upcoming",
                "salesPerson": f"{user.first_name} {user.last_name}" if user else "Unknown",
                "salesPersonId": user.id if user else None,
                "duration": m.duration,
                "notes": m.title
            })
        
        return jsonify({
            "meetings": meetings_list,
            "pagination": {
                "total": pagination.total,
                "pages": pagination.pages,
                "current_page": page,
                "per_page": per_page
            }
        }), 200
    except Exception as e:
        print(f"Error fetching meetings: {str(e)}")
        return jsonify({"error": f"Error fetching meetings: {str(e)}"}), 500


@meetings_bp.route("/admin/<int:meeting_id>", methods=["GET"])
@admin_required
def admin_get_meeting(meeting_id):
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404

    client = Client.query.get(meeting.client_id)
    user = User.query.get(meeting.user_id)

    return jsonify({
        "id": meeting.id,
        "client": client.company_name if client else "Unknown",
        "contactPerson": client.contact_person if client else "N/A",
        "meetingType": meeting.meeting_type,
        "date": meeting.scheduled_date.isoformat(),
        "time": meeting.scheduled_time.strftime('%H:%M'),
        "location": meeting.location.get("label") if meeting.location else meeting.location,
        "status": "Completed" if meeting.scheduled_date < datetime.now().date() else "Upcoming",
        "salesPerson": f"{user.first_name} {user.last_name}" if user else "Unknown",
        "duration": meeting.duration,
        "notes": meeting.title,
        "pastMeetings": []
    }), 200


@meetings_bp.route("/admin/<int:meeting_id>/update", methods=["PUT"])
@admin_required
def admin_update_meeting(meeting_id):
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404

    data = request.get_json()
    
    title = data.get("notes") or data.get("title")
    duration = data.get("duration", meeting.duration)
    location_str = data.get("location")
    meeting_type = data.get("meetingType") or data.get("meeting_type", meeting.meeting_type)
    date_str = data.get("date", meeting.scheduled_date.isoformat())
    time_str = data.get("time", meeting.scheduled_time.strftime('%H:%M'))

    if not all([title, duration, location_str, date_str, time_str]):
        return jsonify({"error": "All fields are required"}), 400

    try:
        duration = int(duration)
        if duration <= 0:
            return jsonify({"error": "Duration must be greater than zero"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Duration must be a valid integer"}), 400

    try:
        meeting_date = datetime.fromisoformat(date_str).date()
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        meeting_datetime = datetime.combine(meeting_date, time_obj)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid date or time format"}), 400

    if location_str != (meeting.location.get("label") if meeting.location else None):
        location = geocode_address(location_str)
        if not location:
            return jsonify({"error": "Could not geocode the provided address"}), 400
        meeting.location = location

    meeting.title = title
    meeting.duration = duration
    meeting.meeting_type = meeting_type
    meeting.scheduled_time = meeting_datetime
    meeting.scheduled_date = meeting_date

    try:
        db.session.commit()
        return jsonify({
            "message": "Meeting updated successfully",
            "meeting": {
                "id": meeting.id,
                "title": meeting.title,
                "duration": meeting.duration,
                "location": meeting.location,
                "meeting_type": meeting.meeting_type,
                "scheduled_time": meeting.scheduled_time.isoformat(),
                "scheduled_date": meeting.scheduled_date.isoformat(),
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500


@meetings_bp.route("/admin/<int:meeting_id>/delete", methods=["DELETE"])
@admin_required
def admin_delete_meeting(meeting_id):
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404

    try:
        db.session.delete(meeting)
        db.session.commit()
        return jsonify({"message": "Meeting deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500


@meetings_bp.route("/sales/create", methods=["POST"])
@sales_or_admin_required
def sales_create_meeting():
    current_user_id = int(get_jwt_identity())

    data = request.get_json() 
    company_name = data.get("companyName") or data.get("company")
    contact_person = data.get("contactPerson")
    meeting_type = data.get("meetingType")
    date_str = data.get("date")
    time_str = data.get("time")
    location_str = data.get("location")
    notes = data.get("notes", "")

    if not all([company_name, contact_person, meeting_type, date_str, time_str, location_str]):
        return jsonify({
            "error": "All fields are required",
            "required": ["companyName", "contactPerson", "meetingType", "date", "time", "location"]
        }), 400

    client = Client.query.filter_by(company_name=company_name, assigned_to=current_user_id).first()
    
    if not client:
        meeting_location = geocode_address(location_str)
        if not meeting_location:
            return jsonify({"error": "Could not geocode the provided address"}), 400
        
        client = Client(
            company_name=company_name,
            contact_person=contact_person,
            phone_number="N/A",
            email="N/A",
            address=location_str,
            status="active",
            location=meeting_location,
            assigned_to=current_user_id
        )
        db.session.add(client)
        db.session.flush()  
    else:
        meeting_location = client.location

    try:
        meeting_date = datetime.fromisoformat(date_str).date()
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        meeting_datetime = datetime.combine(meeting_date, time_obj)
        duration = 60 
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time"}), 400

    try:
        new_meeting = Meeting(
            user_id=current_user_id,
            client_id=client.id,
            title=notes or f"Meeting with {company_name}",
            duration=duration,
            location=meeting_location,
            meeting_type=meeting_type.lower(),
            scheduled_time=meeting_datetime,
            scheduled_date=meeting_date
        )

        db.session.add(new_meeting)
        db.session.commit()

        return jsonify({
            "message": "Meeting created successfully",
            "meeting": {
                "id": new_meeting.id,
                "client": company_name,
                "contactPerson": contact_person,
                "meetingType": new_meeting.meeting_type,
                "date": new_meeting.scheduled_date.isoformat(),
                "time": new_meeting.scheduled_time.strftime('%H:%M'),
                "location": new_meeting.location.get("label") if new_meeting.location else location_str,
                "status": "Upcoming",
                "duration": new_meeting.duration,
                "notes": new_meeting.title
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500


@meetings_bp.route("/sales/my_meetings", methods=["GET"])
@sales_or_admin_required
def sales_get_my_meetings():
    current_user_id = int(get_jwt_identity())
    user_role = get_jwt().get('role')

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status_filter = request.args.get('status', 'all')
    search_term = request.args.get('search', '')

    if page < 1 or per_page < 1 or per_page > 100:
        return jsonify({"error": "Invalid pagination parameters"}), 400

    try:
        if user_role == 'admin':
            query = Meeting.query
        else:
            query = Meeting.query.filter_by(user_id=current_user_id)
        if status_filter == 'upcoming':
            query = query.filter(Meeting.scheduled_date >= datetime.now().date())
        elif status_filter == 'completed':
            query = query.filter(Meeting.scheduled_date < datetime.now().date())

        if search_term:
            query = query.join(Client).filter(
                Client.company_name.ilike(f"%{search_term}%")
            )

        pagination = query.order_by(Meeting.scheduled_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        meetings_list = []
        for m in pagination.items:
            client = Client.query.get(m.client_id)
            user = User.query.get(m.user_id)
            
            meetings_list.append({
                "id": m.id,
                "client": client.company_name if client else "Unknown",
                "contactPerson": client.contact_person if client else "N/A",
                "meetingType": m.meeting_type,
                "date": m.scheduled_date.isoformat(),
                "time": m.scheduled_time.strftime('%H:%M'),
                "location": m.location.get("label") if m.location else m.location,
                "status": "Completed" if m.scheduled_date < datetime.now().date() else "Upcoming",
                "salesPerson": f"{user.first_name} {user.last_name}" if user else "Unknown",
                "duration": m.duration,
                "notes": m.title,
                "pastMeetings": []
            })
        
        return jsonify({
            "meetings": meetings_list,
            "pagination": {
                "total": pagination.total,
                "pages": pagination.pages,
                "current_page": page,
                "per_page": per_page
            }
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error fetching meetings: {str(e)}"}), 500


@meetings_bp.route("/sales/<int:meeting_id>", methods=["GET"])
@sales_or_admin_required
def sales_get_meeting(meeting_id):
    current_user_id = int(get_jwt_identity())
    user_role = get_jwt().get('role')

    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404

    if user_role != 'admin' and meeting.user_id != current_user_id:
        return jsonify({"error": "Access denied"}), 403

    client = Client.query.get(meeting.client_id)

    return jsonify({
        "id": meeting.id,
        "client": client.company_name if client else "Unknown",
        "contactPerson": client.contact_person if client else "N/A",
        "meetingType": meeting.meeting_type,
        "date": meeting.scheduled_date.isoformat(),
        "time": meeting.scheduled_time.strftime('%H:%M'),
        "location": meeting.location.get("label") if meeting.location else meeting.location,
        "status": "Completed" if meeting.scheduled_date < datetime.now().date() else "Upcoming",
        "duration": meeting.duration,
        "notes": meeting.title,
        "pastMeetings": []
    }), 200

@meetings_bp.route("/sales/today", methods=["GET"])
@sales_or_admin_required
def sales_get_todays_meetings():
    current_user_id = int(get_jwt_identity())
    user_role = get_jwt().get('role')
    
    today = datetime.now().date()
    
    try:
        if user_role == 'admin':
            meetings = Meeting.query.filter(
                Meeting.scheduled_date == today
            ).order_by(Meeting.scheduled_time.asc()).all()
        else:
            meetings = Meeting.query.filter(
                Meeting.scheduled_date == today,
                Meeting.user_id == current_user_id
            ).order_by(Meeting.scheduled_time.asc()).all()
        
        meetings_list = []
        for m in meetings:
            client = Client.query.get(m.client_id)
            user = User.query.get(m.user_id)
            
            meetings_list.append({
                "id": m.id,
                "client": client.company_name if client else "Unknown",
                "clientId": client.id if client else None,
                "contactPerson": client.contact_person if client else "N/A",
                "meetingType": m.meeting_type,
                "date": m.scheduled_date.isoformat(),
                "time": m.scheduled_time.strftime('%H:%M'),
                "location": m.location.get("label") if m.location else m.location,
                "status": "Completed" if m.scheduled_date < datetime.now().date() else "Upcoming",
                "duration": m.duration,
                "notes": m.title,
                "salesPerson": f"{user.first_name} {user.last_name}" if user else "Unknown"
            })
        
        return jsonify({
            "meetings": meetings_list,
            "count": len(meetings_list)
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Error fetching today's meetings: {str(e)}"}), 500


@meetings_bp.route("/sales/<int:meeting_id>/update", methods=["PUT"])
@sales_or_admin_required
def sales_update_meeting(meeting_id):
    current_user_id = int(get_jwt_identity())
    user_role = get_jwt().get('role')

    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404

    if user_role != 'admin' and meeting.user_id != current_user_id:
        return jsonify({"error": "Access denied"}), 403

    data = request.get_json()
    title = data.get("notes") or data.get("title", meeting.title)
    duration = data.get("duration", meeting.duration)
    location_str = data.get("location")
    meeting_type = data.get("meetingType") or data.get("meeting_type", meeting.meeting_type)
    date_str = data.get("date", meeting.scheduled_date.isoformat())
    time_str = data.get("time", meeting.scheduled_time.strftime('%H:%M'))

    if not all([title, duration, location_str, date_str, time_str]):
        return jsonify({"error": "All fields are required"}), 400

    try:
        duration = int(duration)
        if duration <= 0:
            return jsonify({"error": "Duration must be greater than zero"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Duration must be a valid integer"}), 400

    try:
        meeting_date = datetime.fromisoformat(date_str).date()
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        meeting_datetime = datetime.combine(meeting_date, time_obj)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid date or time format"}), 400

    if location_str != (meeting.location.get("label") if meeting.location else None):
        location = geocode_address(location_str)
        if not location:
            return jsonify({"error": "Could not geocode the provided address"}), 400
        meeting.location = location

    meeting.title = title
    meeting.duration = duration
    meeting.meeting_type = meeting_type
    meeting.scheduled_time = meeting_datetime
    meeting.scheduled_date = meeting_date

    try:
        db.session.commit()
        return jsonify({
            "message": "Meeting updated successfully",
            "meeting": {
                "id": meeting.id,
                "title": meeting.title,
                "duration": meeting.duration,
                "location": meeting.location,
                "meeting_type": meeting.meeting_type,
                "scheduled_time": meeting.scheduled_time.isoformat(),
                "scheduled_date": meeting.scheduled_date.isoformat(),
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
        
@meetings_bp.route("client/<int:client_id>/", methods=["GET"])
@owner_or_admin_required
def get_meetings_for_client(client_id):
    try:
        client = Client.query.get(client_id)
        if not client:
            return jsonify({"error": "Client not found"}), 404

        today = datetime.utcnow().date()
        meetings = Meeting.query.filter_by(client_id=client_id).order_by(Meeting.scheduled_date.desc()).all()

        upcoming = []
        past = []

        for m in meetings:
            meeting_data = {
                "id": m.id,
                "title": m.title,
                "meetingType": m.meeting_type,
                "scheduled_date": m.scheduled_date.isoformat(),
                "scheduled_time": m.scheduled_time.strftime('%H:%M'),
                "duration": m.duration,
                "location": m.location.get("label") if m.location else m.location,
                "status": "Completed" if m.scheduled_date < today else "Upcoming"
            }
            if m.scheduled_date >= today:
                upcoming.append(meeting_data)
            else:
                past.append(meeting_data)

        return jsonify({
            "client_id": client_id,
            "upcomingMeetings": upcoming,
            "pastMeetings": past
        }), 200

    except Exception as e:
        return jsonify({"error": f"Error fetching client meetings: {str(e)}"}), 500




@meetings_bp.route("/sales/<int:meeting_id>/delete", methods=["DELETE"])
@sales_or_admin_required
def sales_delete_meeting(meeting_id):
    current_user_id = int(get_jwt_identity())
    user_role = get_jwt().get('role')

    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        return jsonify({"error": "Meeting not found"}), 404

    if user_role != 'admin' and meeting.user_id != current_user_id:
        return jsonify({"error": "Access denied"}), 403

    try:
        db.session.delete(meeting)
        db.session.commit()
        return jsonify({"message": "Meeting deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500