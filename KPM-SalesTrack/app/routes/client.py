from flask import Blueprint,jsonify,request,send_from_directory
from app.models import Client
from app.db import db
from datetime import datetime

clients_bp = Blueprint("clients", __name__)

@clients_bp.route("/create", methods=["POST"])
def create_client():
    data = request.get_json()

    company_name = data.get("company_name")
    contact_person = data.get("contact_person")
    phone_number = data.get("phone_number")
    email = data.get("email")
    address = data.get("address")
    status = data.get("status")
    location = data.get("location")
    created_at = data.get("created_at", datetime.utcnow().isoformat())
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
    if not location:
        return jsonify({"error": "Location is required"}), 400
    if not created_at:
        return jsonify({"error": "Created at date is required"}), 400
    if not assigned_to:
        return jsonify({"error": "Assigned to is required"}), 400

    new_client = Client(
        company_name=company_name,
        contact_person=contact_person,
        phone_number=phone_number,
        email=email,
        address=address,
        status=status,
        location=location,
        created_at=datetime.fromisoformat(created_at) if isinstance(created_at, str) else created_at,
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

@clients_bp.route("/get_client/", methods=["GET"])
def get_client(client_id):
    client = Client.query.get(client_id)

    if not client:
        return jsonify({"error": "Client not found"}), 404

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
        "assigned_to": client.assigned_to
    }), 201

@clients_bp.route("/edit", methods=["PUT"])
def edit_client(client_id):
    data = request.get_json()
    client = Client.query.get(client_id)

    if not client:
        return jsonify({"error": "Client not found"}), 404

    
    db.session.edit(client)
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
    }), 201

@clients_bp.route("/hard_delete", methods=["DELETE"])
def delete_client(client_id):
    client = Client.query.get(client_id)

    if not client:
        return jsonify({"error": "Client not found"}), 404

    db.session.delete(client)
    db.session.commit()

    return jsonify({"message": "Client deleted successfully"}), 200

@clients_bp.route("/soft_delete", methods=["DELETE"])
def soft_delete_clients():
    client_ids = request.get_json().get("client_ids", [])

    if not client_ids:
        return jsonify({"error": "No client IDs provided"}), 400

    clients = Client.query.filter(Client.id.in_(client_ids)).all()

    if not clients:
        return jsonify({"error": "No clients found for the provided IDs"}), 404

    for client in clients:
        db.session.delete(client)

    db.session.commit()

    return jsonify({"message": "Clients deleted successfully"}), 200

@clients_bp.route("/restore", methods=["PATCH"])
def restore_client(client_id):
    client = Client.query.get(client_id)

    if not client:
        return jsonify({"error": "Client not found"}), 404

    client.is_deleted = False
    db.session.commit()

    return jsonify({
        "message": "Client restored successfully",
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
    }), 201