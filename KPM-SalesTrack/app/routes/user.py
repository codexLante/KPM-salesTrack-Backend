from flask import Blueprint,jsonify,request,send_from_directory
from app.models import Users
from app.db import db
import re
import os
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token
from datetime import timedelta

bcrypt = Bycrypt()

users_bp=Blueprint("users",__name__)

@users_bp.route("/add",methods=["POST"])
def add_users():
  data=request.get_json()
  first_name=data.get("first_name")
  last_name=data.get("last_name")
  email=data.get("email")
  password=data.get("password")
  is_active=data.get("is_active")
  created_at=data.get("created_at")

  if not first_name:
    return jsonify({"error":"First name is required"}),400
  if not last_name:
    return jsonify({"error":"Last name is required"}),400
  if not email:
    return jsonify({"error":"Email is required"}),400

    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    if not re.match(email_regex, email):
        return jsonify({"error": "Invalid email address"})

  if not password:
    return jsonify({"error":"Password is required"}),400

  exists=users.query.filter_by(email=email).first()
  if exists:
    return jsonify({"error":"User with this email already exists"}),400

  hashed_password = bycrypt.generate_password_hash(password).decode('utf-8')

  new_users = users(username=username,email=email,password=hashed_password,is_active=is_active,created_at=created_at)
  db.session.add(new_user)
  db.session.commit()

  access_token = create_access_token(
    identity=str(new_users.id),
    additional_claims={"email": new_users.email},
    expires_delta=timedelta(hours=1)
  )

  return jsonify({
    "message": "User created successfully",
    "token": access_token,
    "user": {
      "id" : new_users.id,
      "first_name": new_users.first_name,
      "last_name": new_users.last_name,
      "email": new_users.email,
      "is_active": new_users.is_active,
      "created_at": new_users.created_at
    }
  })

  @users_bp.route("/login", methods=["POST"])
  def login_users():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
      return jsonify({"error": "Email and password are required"}), 400

    users = users.query.filter_by(email=email).first()

    if not users:
      return jsonify({"error": "user not found"}), 401

    check_password = bcrypt.check_password_hash(users.password, password)

    if not check_password:
      return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(
      identity=str(users.id),
      additional_claims={"email": new_users.email},
      expires_delta=timedelta(hours=1)
    )

    return jsonify({
      "token": access_token,
      "user": {
        "id": users.id,
        "first_name": users.first_name,
        "last_name": users.last_name,
        "email": users.email,
        "is_active": users.is_active,
        "created_at": users.created_at
      }
    }), 200
