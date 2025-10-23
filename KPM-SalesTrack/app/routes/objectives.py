from flask import Blueprint, jsonify, request
from app.models import Objective
from app.db import db
from datetime import datetime



objectives_bp = Blueprint('objectives', __name__)


@objectives_bp.route('/create', methods=['POST'])
def create_objective():
    data = request.get_json()
    
    title = data.get('title')
    description = data.get('description')
    target_value = data.get('target_value')
    start_time = data.get('start_time')# to change to stat_date
    end_time = data.get('end_time') # to change to end_date 
    user_id = data.get('user_id')
    created_by = data.get('created_by')

    if not title:
        return jsonify({"error": "Title is required"}), 400
    if not target_value or not isinstance(target_value, int):
        return jsonify({"error": "Target value must be a valid integer"}), 400
    if not start_time or not isinstance(start_time, str):
        return jsonify({"error": "Start time must be a valid ISO format string"}), 400
    if not end_time or not isinstance(end_time, str):
        return jsonify({"error": "End time must be a valid ISO format string"}), 400
    if not user_id or not isinstance(user_id, int):
        return jsonify({"error": "User ID must be a valid integer"}), 400
    if not created_by or not isinstance(created_by, int):
        return jsonify({"error": "Created by must be a valid integer"}), 400

    new_objective = Objective(
        title=title,
        description=description,
        target_value=target_value,
        start_time=start_time,
        end_time=end_time,
        user_id=user_id,
        created_by=created_by
    )

    db.session.add(new_objective)
    db.session.commit()

    return jsonify({
        "message": "Objective created successfully",
        "objective": {
            "id": new_objective.id,
            "title": new_objective.title,
            "description": new_objective.description,
            "target_value": new_objective.target_value,
            "current_value": new_objective.current_value,
            "start_time": new_objective.start_time.isoformat(),
            "end_time": new_objective.end_time.isoformat(),
            "user_id": new_objective.user_id,
            "created_by": new_objective.created_by
        }
    }), 201

@objectives_bp.route('/GetAll', methods=['GET'])
def get_all_objectives():
    objectives = Objective.query.all()
    objectives_list = [{
        "id": obj.id,
        "title": obj.title,
        "description": obj.description,
        "target_value": obj.target_value,
        "current_value": obj.current_value,
        "start_time": obj.start_time.isoformat(),
        "end_time": obj.end_time.isoformat(),
        "user_id": obj.user_id,
        "created_by": obj.created_by,
        "created_at": obj.created_at.isoformat()
    } for obj in objectives]
    return jsonify(objectives_list), 200

@objectives_bp.route('/<int:objective_id>/updated', methods=['PUT'])
def updated_objective(objective_id):
    objective = objective.query.get(objective_id)
    if not objective:
        return jsonify({"error": "Objective not found"}), 400
        
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    target_value = data.get('target_value')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    user_id = data.get('user_id') 
    created_by = data.get('created_by')

    if not title:
        return jsonify({"error": "Title is required"}), 400
    if not target_value or not isinstance(target_value, int):
        return jsonify({"error": "Target value must be a valid integer"}), 400
    if not start_time or not isinstance(start_time, str):
        return jsonify({"error": "Start time must be a valid ISO format string"}), 400
    if not end_time or not isinstance(end_time, str):
        return jsonify({"error": "End time must be a valid ISO format string"}), 400
    if not user_id or not isinstance(user_id, int):
        return jsonify({"error": "User ID must be a valid integer"}), 400
    if not created_by or not isinstance(created_by, int):
        return jsonify({"error": "Created by must be a valid integer"}), 400

    Updated_objective = Objective(
        title=title,
        description=description,
        target_value=target_value,
        start_time=start_time,
        end_time=end_time,
        user_id=user_id,
        created_by=created_by
    )

    db.session.add(Updated_objective)
    db.session.commit()

    return jsonify({
        "message": "Objective updated successfully",
        "objective": {
            "id": Updated_objective.id,
            "title": Updated_objective.title,
            "description": Updated_objective.description,
            "target_value": Updated_objective.target_value,
            "current_value": Updated_objective.current_value,
            "start_time": Updated_objective.start_time.isoformat(),
            "end_time": Updated_objective.end_time.isoformat,
            "user_id": Updated_objective.user_id,
            "created_by": Updated_objective.created_by,
            "created_at": Updated_objective.created_at.isoformat()
        }
    }), 200
    
    