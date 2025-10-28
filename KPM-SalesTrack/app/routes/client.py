from flask import Blueprint, jsonify, request
from app.models import Client
from app.db import db
from datetime import datetime
from app.utils import geocode_address

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
    }), 200

@clients_bp.route("/<int:client_id>/edit", methods=["PUT"])
def edit_client(client_id):
    data = request.get_json()
    client = Client.query.get(client_id)

    if not client:
        return jsonify({"error": "Client not found"}), 404

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
def get_all_clients():
    clients = Client.query.all()
    clients_list = []

    for client in clients:
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
    return jsonify(clients_list), 200

@clients_bp.route("/<int:client_id>/hard_delete", methods=["DELETE"])
def delete_client(client_id):
    client = Client.query.get(client_id)

    if not client:
        return jsonify({"error": "Client not found"}), 404

    db.session.delete(client)
    db.session.commit()

    return jsonify({"message": "Client deleted successfully"}), 200