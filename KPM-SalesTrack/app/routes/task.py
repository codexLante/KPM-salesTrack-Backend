from flask import Blueprint, jsonify, request
from app.models import Task
from app.db import db
from datetime import datetime
from flask_jwt_extended import get_jwt_identity, get_jwt
from app.utils import admin_required, owner_or_admin_required

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/add", methods=["POST"])
@admin_required
def add_task():
    data = request.get_json()
    
    title = data.get("title")
    description = data.get("description")
    due_date = data.get("due_date")
    assigned_to = data.get("assigned_to")
    assigned_by = data.get("assigned_by")
    status = data.get("status", "pending")

    if not title or not description:
        return jsonify({"error": "Title and description are required"}), 400
    if not isinstance(assigned_to, int) or not isinstance(assigned_by, int):
        return jsonify({"error": "Assigned fields must be integers"}), 400

    current_user_id = int(get_jwt_identity())
    if assigned_by != current_user_id:
        return jsonify({"error": "You can only assign tasks as yourself"}), 403

    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = datetime.fromisoformat(due_date)
        except ValueError:
            return jsonify({"error": "Due date must be a valid ISO format string"}), 400

    new_task = Task(
        title=title,
        description=description,
        due_date=parsed_due_date,
        assigned_to=assigned_to,
        assigned_by=assigned_by,
        status=status,
    )
    
    db.session.add(new_task)
    db.session.commit()

    return jsonify({
        "message": "Task created successfully",
        "task": {
            "id": new_task.id,
            "title": new_task.title,
            "description": new_task.description,
            "status": new_task.status,
            "assigned_to": new_task.assigned_to,
            "assigned_by": new_task.assigned_by,
            "due_date": new_task.due_date.isoformat() if new_task.due_date else None,
            "created_at": new_task.created_at.isoformat()
        }
    }), 201


@tasks_bp.route("/GetAll", methods=["GET"])
@admin_required
def get_all_tasks():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        if page < 1:
            return jsonify({"error": "Page must be >= 1"}), 400
        if per_page < 1 or per_page > 100:
            return jsonify({"error": "Per page must be between 1 and 100"}), 400
        
        pagination = Task.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        tasks_list = [{
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "assigned_to": task.assigned_to,
            "assigned_by": task.assigned_by,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "created_at": task.created_at.isoformat()
        } for task in pagination.items]
        
        return jsonify({
            "tasks": tasks_list,
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
        return jsonify({"error": f"Failed to retrieve tasks: {str(e)}"}), 500


@tasks_bp.route("/get/<int:task_id>", methods=["GET"])
@owner_or_admin_required
def get_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    current_user_id = int(get_jwt_identity())
    role = get_jwt().get("role")
    
    if role != "admin" and task.assigned_to != current_user_id:
        return jsonify({"error": "Access denied. You can only view your own tasks."}), 403
    
    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "assigned_to": task.assigned_to,
        "assigned_by": task.assigned_by,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "created_at": task.created_at.isoformat()
    }), 200


@tasks_bp.route("/update/<int:task_id>", methods=["PUT"])
@owner_or_admin_required
def update_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    current_user_id = int(get_jwt_identity())
    role = get_jwt().get("role")
    
    if role != "admin" and task.assigned_to != current_user_id:
        return jsonify({"error": "Access denied. You can only update your own tasks."}), 403

    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    due_date = data.get("due_date")
    assigned_to = data.get("assigned_to")
    assigned_by = data.get("assigned_by")
    status = data.get("status")

    if not title or not description or not assigned_to or not assigned_by:
        return jsonify({"error": "All fields are required"}), 400

    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = datetime.fromisoformat(due_date)
        except ValueError:
            return jsonify({"error": "Due date must be a valid ISO format string"}), 400

    task.title = title
    task.description = description
    task.due_date = parsed_due_date
    task.assigned_to = assigned_to
    task.assigned_by = assigned_by
    task.status = status

    db.session.commit()

    return jsonify({
        "message": "Task updated successfully",
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "assigned_to": task.assigned_to,
            "assigned_by": task.assigned_by,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "created_at": task.created_at.isoformat()
        }
    }), 200


@tasks_bp.route("/permanent/<int:task_id>", methods=["DELETE"])
@admin_required
def permanent_delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    db.session.delete(task)
    db.session.commit()

    return jsonify({"message": "Task permanently deleted"}), 200