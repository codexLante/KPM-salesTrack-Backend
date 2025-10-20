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
