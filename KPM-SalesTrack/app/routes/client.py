from flask import Blueprint, jsonify, request
from app.models import Client,Meeting
from app.db import db
from datetime import datetime
from app.utils import geocode_address, admin_required, salesman_required, owner_or_admin_required
from flask_jwt_extended import get_jwt_identity, get_jwt

clients_bp = Blueprint("clients", __name__)


@clients_bp.route("/create", methods=["POST"])
@salesman_required
def create_client():
    data = request.get_json()

    company_name = data.get("company_name")
    contact_person = data.get("contact_person")
    phone_number = data.get("phone_number")
    email = data.get("email")
    address = data.get("address")
    status = data.get("status")
    assigned_to = data.get("assigned_to")
    
    current_user_id = int(get_jwt_identity())
    role = get_jwt().get("role")

    if role != "admin" and assigned_to != current_user_id:
        return jsonify({"error": "You can only assign clients to yourself"}), 403

    if not company_name:
        return jsonify({"error": "Company name is required"}), 400
    if not contact_person:
        return jsonify({"error": "Contact person is required"}), 400
    if not phone_number:
        return jsonify({"error": "Phone number is required"}), 400
    if not email:
        return jsonify({"error": "Email is required"}), 400
    if not address:
        return jsonify({"error": "Address is required"}), 400
    if not status:
        return jsonify({"error": "Status is required"}), 400
    if not assigned_to:
        return jsonify({"error": "Assigned to is required"}), 400

    location = geocode_address(address)
    if not location:
        return jsonify({"error": "Could not geocode the provided address"}), 400

    new_client = Client(
        company_name=company_name,
        contact_person=contact_person,
        phone_number=phone_number,
        email=email,
        address=address,
        status=status,
        location=location,
        assigned_to=assigned_to
    )

    db.session.add(new_client)
    db.session.commit()

    return jsonify({
        "message": "Client created successfully",
        "client": {
            "id": new_client.id,
            "company_name": new_client.company_name,
            "contact_person": new_client.contact_person,
            "phone_number": new_client.phone_number,
            "email": new_client.email,
            "address": new_client.address,
            "status": new_client.status,
            "location": new_client.location,
            "created_at": new_client.created_at.isoformat(),
            "assigned_to": new_client.assigned_to
        },
    }), 201


@clients_bp.route("/<int:client_id>/get", methods=["GET"])
@owner_or_admin_required
def get_client(client_id):
    client = Client.query.get(client_id)
    if not client:
        return jsonify({"error": "Client not found"}), 404

    current_user_id = int(get_jwt_identity())
    role = get_jwt().get("role")
    if role != "admin" and client.assigned_to != current_user_id:
        return jsonify({"error": "Access denied"}), 400

    today = datetime.utcnow().date()
    meetings = Meeting.query.filter_by(client_id=client.id).order_by(Meeting.scheduled_date.desc()).all()

    upcoming = []
    past = []

    for m in meetings:
        meeting_data = {
            "id": m.id,
            "type": m.meeting_type,
            "title": m.title,
            "scheduled_date": m.scheduled_date.isoformat(),
            "scheduled_time": m.scheduled_time.strftime("%H:%M"),
            "duration": m.duration,
            "location": m.location,
        }
        if m.scheduled_date >= today:
            upcoming.append(meeting_data)
        else:
            past.append(meeting_data)

    return jsonify({
        "id": client.id,
        "company_name": client.company_name,
        "contact_person": client.contact_person,
        "phone_number": client.phone_number,
        "email": client.email,
        "address": client.address,
        "status": client.status,
        "location": client.location,
        "created_at": client.created_at.isoformat(),
        "assigned_to": client.assigned_to,
        "upcomingMeetings": upcoming,
        "pastMeetings": past
    }), 200

@clients_bp.route("/<int:client_id>/edit", methods=["PUT"])
@owner_or_admin_required
def edit_client(client_id):
    data = request.get_json()
    client = Client.query.get(client_id)

    if not client:
        return jsonify({"error": "Client not found"}), 404
    
    current_user_id = int(get_jwt_identity())
    role = get_jwt().get("role")
    
    if role != "admin" and client.assigned_to != current_user_id:
        return jsonify({"error": "Access denied. You can only edit your own clients."}), 400

    company_name = data.get("company_name")
    contact_person = data.get("contact_person")
    phone_number = data.get("phone_number")
    email = data.get("email")
    address = data.get("address")
    status = data.get("status")
    assigned_to = data.get("assigned_to")

    if not company_name:
        return jsonify({"error": "Company name is required"}), 400
    if not contact_person:
        return jsonify({"error": "Contact person is required"}), 400
    if not phone_number:
        return jsonify({"error": "Phone number is required"}), 400
    if not email:
        return jsonify({"error": "Email is required"}), 400
    if not address:
        return jsonify({"error": "Address is required"}), 400
    if not status:
        return jsonify({"error": "Status is required"}), 400
    if not assigned_to:
        return jsonify({"error": "Assigned to is required"}), 400

    if address != client.address:
        location = geocode_address(address)
        if not location:
            return jsonify({"error": "Could not geocode the updated address"}), 400
        client.location = location

    client.company_name = company_name
    client.contact_person = contact_person
    client.phone_number = phone_number
    client.email = email
    client.address = address
    client.status = status
    client.assigned_to = assigned_to

    db.session.commit()

    return jsonify({
        "message": "Client updated successfully",
        "client": {
            "id": client.id,
            "company_name": client.company_name,
            "contact_person": client.contact_person,
            "phone_number": client.phone_number,
            "email": client.email,
            "address": client.address,
            "status": client.status,
            "location": client.location,
            "created_at": client.created_at.isoformat(),
            "assigned_to": client.assigned_to
        }
    }), 200


@clients_bp.route("/GetAll", methods=["GET"])
@admin_required
def get_all_clients():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        if page < 1:
            return jsonify({"error": "Page must be >= 1"}), 400
        if per_page < 1 or per_page > 100:
            return jsonify({"error": "Per page must be between 1 and 100"}), 400
        
        pagination = Client.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        clients_list = []
        for client in pagination.items:
            clients_list.append({
                "id": client.id,
                "company_name": client.company_name,
                "contact_person": client.contact_person,
                "phone_number": client.phone_number,
                "email": client.email,
                "address": client.address,
                "status": client.status,
                "location": client.location,
                "created_at": client.created_at.isoformat(),
                "assigned_to": client.assigned_to
            })
        
        return jsonify({
            "clients": clients_list,
            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev
            }
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve clients: {str(e)}"}), 500


@clients_bp.route("/my_clients", methods=["GET"])
@salesman_required
def get_my_clients():
    try:
        current_user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        if page < 1:
            return jsonify({"error": "Page must be >= 1"}), 400
        if per_page < 1 or per_page > 100:
            return jsonify({"error": "Per page must be between 1 and 100"}), 400
    
        pagination = Client.query.filter_by(assigned_to=current_user_id).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        clients_list = [{
            "id": c.id,
            "company_name": c.company_name,
            "contact_person": c.contact_person,
            "phone_number": c.phone_number,
            "email": c.email,
            "address": c.address,
            "status": c.status,
            "location": c.location,
            "created_at": c.created_at.isoformat(),
            "assigned_to": c.assigned_to
        } for c in pagination.items]
        
        return jsonify({
            "clients": clients_list,
            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev
            }
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve clients: {str(e)}"}), 500


@clients_bp.route("/<int:client_id>/hard_delete", methods=["DELETE"])
@owner_or_admin_required
def delete_client(client_id):
    client = Client.query.get(client_id)

    if not client:
        return jsonify({"error": "Client not found"}), 404
    current_user_id = int(get_jwt_identity())
    role = get_jwt().get("role")
    
    if role != "admin" and client.assigned_to != current_user_id:
        return jsonify({"error": "Access denied. You can only delete your own clients."}), 403

    db.session.delete(client)
    db.session.commit()

    return jsonify({"message": "Client deleted successfully"}), 200