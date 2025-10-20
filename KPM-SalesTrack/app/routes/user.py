from flask import Blueprint,jsonify,request,send_from_directory
from app.models import Users
from app.db import db
import re
import os
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token
from datetime import timedelta