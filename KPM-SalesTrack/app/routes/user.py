from flask import Blueprint,jsonify,request
from app.models import User
from app.db import db
import re
import os
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token
from datetime import timedelta

bcrypt = Bcrypt()

users_bp = Blueprint("users", __name__)

@users_bp.route("/add", methods=["POST"])
def add_users():
    data = request.get_json()
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    password = data.get("password")
    phone_number = data.get("phone_number") 
    role = data.get("role", "user")  

    
    if not first_name:
        return jsonify({"error": "First name is required"}), 400
    if not last_name:
        return jsonify({"error": "Last name is required"}), 400
    if not email:
        return jsonify({"error": "Email is required"}), 400
    if not phone_number:
        return jsonify({"error": "Phone number is required"}), 400

    
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_regex, email):
        return jsonify({"error": "Invalid email address"}), 400

    if not password:
        return jsonify({"error": "Password is required"}), 400
    
    
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters long"}), 400

    
    exists = User.query.filter_by(email=email).first()
    if exists:
        return jsonify({"error": "User with this email already exists"}), 400

    
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    
    new_user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=hashed_password,
        phone_number=phone_number,
        role=role
    )
    
    
    db.session.add(new_user)
    db.session.commit()
    

    
    access_token = create_access_token(
        identity=str(new_user.id),
        additional_claims={"email": new_user.email, "role": new_user.role},
        expires_delta=timedelta(hours=1)
    )

    return jsonify({
        "message": "User created successfully",
        "token": access_token,
        "user": {
            "id": new_user.id,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "email": new_user.email,
            "phone_number": new_user.phone_number,
            "role": new_user.role,
            "is_active": new_user.is_active,
            "created_at": new_user.created_at.isoformat() if new_user.created_at else None
        }
    }), 201


@users_bp.route("/login", methods=["POST"])  
def login_users():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

   
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "user not found, kindly sign up"}), 401

    
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Invalid email or password"}), 401

    
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"email": user.email, "role": user.role},
        expires_delta=timedelta(hours=1)
    )

    return jsonify({
        "message": "Login successful",
        "token": access_token,
        "user": {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone_number": user.phone_number,
            "role": user.role
        }
    }), 200