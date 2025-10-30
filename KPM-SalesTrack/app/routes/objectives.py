from flask import Blueprint, jsonify, request
from app.models import Objective
from app.db import db
from datetime import datetime
from flask_jwt_extended import get_jwt_identity, get_jwt
from app.utils import admin_required, salesman_required, owner_or_admin_required

objectives_bp = Blueprint('objectives', __name__)


@objectives_bp.route('/create', methods=['POST'])
@salesman_required
def create_objective():
    data = request.get_json()
    try:
        current_user_id = int(get_jwt_identity())
    except Exception:
        return jsonify({"error": "Authentication error."}), 401
    
    title = data.get('title')
    description = data.get('description')
    target_value = data.get('target_value')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    user_id = data.get('user_id') 

    if not title:
        return jsonify({"error": "Title is required"}), 400
    
    if target_value is None:
        return jsonify({"error": "Target value is required"}), 400
    try:
        target_value = int(target_value)
    except (ValueError, TypeError):
        return jsonify({"error": "Target value must be a valid integer"}), 400
        
    if not start_date or not isinstance(start_date, str):
        return jsonify({"error": "Start date must be a valid ISO format string"}), 400
    if not end_date or not isinstance(end_date, str):
        return jsonify({"error": "End date must be a valid ISO format string"}), 400
    if not user_id or not isinstance(user_id, int):
        return jsonify({"error": "User ID must be a valid integer"}), 400
    try:
        parsed_start_date = datetime.fromisoformat(start_date)
        parsed_end_date = datetime.fromisoformat(end_date)
    except ValueError:
        return jsonify({"error": "Dates must be valid ISO format"}), 400

    new_objective = Objective(
        title=title,
        description=description,
        target_value=target_value,
        start_date=parsed_start_date,
        end_date=parsed_end_date,
        user_id=user_id,
        created_by=current_user_id 
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
            "current_value": getattr(new_objective, 'current_value', 0),
            "start_date": new_objective.start_date.isoformat(),
            "end_date": new_objective.end_date.isoformat(),
            "user_id": new_objective.user_id,
            "created_by": new_objective.created_by
        }
    }), 201


@objectives_bp.route('/GetAll', methods=['GET'])
@admin_required
def get_all_objectives():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        if page < 1:
            return jsonify({"error": "Page must be >= 1"}), 400
        if per_page < 1 or per_page > 100:
            return jsonify({"error": "Per page must be between 1 and 100"}), 400

        pagination = Objective.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        objectives_list = [{
            "id": obj.id,
            "title": obj.title,
            "description": obj.description,
            "target_value": obj.target_value,
            "current_value": obj.current_value,
            "start_date": obj.start_date.isoformat(),
            "end_date": obj.end_date.isoformat(),
            "user_id": obj.user_id,
            "created_by": obj.created_by,
            "created_at": obj.created_at.isoformat()
        } for obj in pagination.items]
        
        return jsonify({
            "objectives": objectives_list,
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
        return jsonify({"error": f"Failed to retrieve objectives: {str(e)}"}), 500


@objectives_bp.route('/my_objectives', methods=['GET'])
@salesman_required
def get_my_objectives():
    try:
        current_user_id = int(get_jwt_identity())
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        if page < 1:
            return jsonify({"error": "Page must be >= 1"}), 400
        if per_page < 1 or per_page > 100:
            return jsonify({"error": "Per page must be between 1 and 100"}), 400
    
        pagination = Objective.query.filter_by(user_id=current_user_id).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        objectives_list = [{
            "id": obj.id,
            "title": obj.title,
            "description": obj.description,
            "target_value": obj.target_value,
            "current_value": obj.current_value,
            "start_date": obj.start_date.isoformat(),
            "end_date": obj.end_date.isoformat(),
            "user_id": obj.user_id,
            "created_by": obj.created_by,
            "created_at": obj.created_at.isoformat()
        } for obj in pagination.items]
        
        return jsonify({
            "objectives": objectives_list,
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
        return jsonify({"error": f"Failed to retrieve objectives: {str(e)}"}), 500


@objectives_bp.route('/<int:objective_id>/get', methods=['GET'])
@owner_or_admin_required
def get_objective(objective_id):
    objective = Objective.query.get(objective_id)
    if not objective:
        return jsonify({"error": "Objective not found"}), 404
    
    current_user_id = int(get_jwt_identity())
    role = get_jwt().get("role")
    
    if role != "admin" and objective.user_id != current_user_id:
        return jsonify({"error": "Access denied. You can only view your own objectives."}), 400

    return jsonify({
        "id": objective.id,
        "title": objective.title,
        "description": objective.description,
        "target_value": objective.target_value,
        "current_value": objective.current_value,
        "start_date": objective.start_date.isoformat(),
        "end_date": objective.end_date.isoformat(),
        "user_id": objective.user_id,
        "created_by": objective.created_by,
        "created_at": objective.created_at.isoformat()
    }), 200


@objectives_bp.route('/<int:objective_id>/updated', methods=['PUT'])
@owner_or_admin_required
def updated_objective(objective_id):
    objective = Objective.query.get(objective_id)
    if not objective:
        return jsonify({"error": "Objective not found"}), 400
    
    current_user_id = int(get_jwt_identity())
    role = get_jwt().get("role")
    
    if role != "admin" and objective.user_id != current_user_id:
        return jsonify({"error": "Access denied. You can only update your own objectives."}), 400

    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    target_value = data.get('target_value')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    user_id = data.get('user_id')
    created_by = data.get('created_by')

    if not title:
        return jsonify({"error": "Title is required"}), 400
    if not target_value or not isinstance(target_value, int):
        return jsonify({"error": "Target value must be a valid integer"}), 400
    if not start_date or not isinstance(start_date, str):
        return jsonify({"error": "Start date must be a valid ISO format string"}), 400
    if not end_date or not isinstance(end_date, str):
        return jsonify({"error": "End date must be a valid ISO format string"}), 400
    if not user_id or not isinstance(user_id, int):
        return jsonify({"error": "User ID must be a valid integer"}), 400
    if not created_by or not isinstance(created_by, int):
        return jsonify({"error": "Created by must be a valid integer"}), 400

    try:
        parsed_start_date = datetime.fromisoformat(start_date)
        parsed_end_date = datetime.fromisoformat(end_date)
    except ValueError:
        return jsonify({"error": "Dates must be valid ISO format"}), 400

    objective.title = title
    objective.description = description
    objective.target_value = target_value
    objective.start_date = parsed_start_date
    objective.end_date = parsed_end_date
    objective.user_id = user_id
    objective.created_by = created_by

    db.session.commit()

    return jsonify({
        "message": "Objective updated successfully",
        "objective": {
            "id": objective.id,
            "title": objective.title,
            "description": objective.description,
            "target_value": objective.target_value,
            "current_value": objective.current_value,
            "start_date": objective.start_date.isoformat(),
            "end_date": objective.end_date.isoformat(),
            "user_id": objective.user_id,
            "created_by": objective.created_by,
            "created_at": objective.created_at.isoformat()
        }
    }), 200


@objectives_bp.route('/<int:objective_id>/delete', methods=['DELETE'])
@owner_or_admin_required
def delete_objective(objective_id):
    objective = Objective.query.get(objective_id)
    if not objective:
        return jsonify({"error": "Objective not found"}), 400
    
    current_user_id = int(get_jwt_identity())
    role = get_jwt().get("role")
    
    if role != "admin" and objective.user_id != current_user_id:
        return jsonify({"error": "Access denied. You can only delete your own objectives."}), 400

    db.session.delete(objective)
    db.session.commit()

    return jsonify({"message": "Objective deleted successfully"}), 200