from flask import Blueprint, jsonify, request
from app.models import Task
from app.db import db
from datetime import datetime

tasks_bp = Blueprint("tasks", __name__)

@tasks_bp.route("/add", methods=["POST"])
def add_task():
    data = request.get_json()
    
    title = data.get("title")
    description = data.get("description")
    due_date = data.get("due_date")
    assigned_to = data.get("assigned_to")
    assigned_by = data.get("assigned_by")
    status = data.get("status", "pending")

    if not title:
        return jsonify({"error": "Title is required"}), 400
    if not description:
        return jsonify({"error": "Description is required"}), 400
    if not isinstance(assigned_to, int) or not isinstance(assigned_by, int):
        return jsonify({"error": "Assigned fields must be integers"}), 400

    
    parsed_due_date = None
    if due_date:
        if not isinstance(due_date, str):
            return jsonify({"error": "Due date must be a valid ISO format string"}), 400
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
def get_all_tasks():
    tasks = Task.query.all()
    tasks_list = []

    for task in tasks:
        tasks_list.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "assigned_to": task.assigned_to,
            "assigned_by": task.assigned_by,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "created_at": task.created_at.isoformat()
        })
    
    return jsonify(tasks_list), 200

@tasks_bp.route("/get/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = Task.query.get(task_id)

    if not task:
        return jsonify({"error": "Task not found"}), 404
    
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
def update_task(task_id):
    data = request.get_json()
    

    task = Task.query.filter_by(id=task_id).first()

    if not task:
        return jsonify({"error": "Task not found"}), 400
    
    title = data.get("title")
    description = data.get("description")
    due_date = data.get("due_date")
    assigned_to = data.get("assigned_to")
    assigned_by = data.get("assigned_by")
    status = data.get("status")

    if not title:
        return jsonify({"error": "Title is required"}), 400
    if not description:
        return jsonify({"error": "Description is required"}), 400
    if not assigned_to:
        return jsonify({"error": "Assigned to is required"}), 400
    if not assigned_by:
        return jsonify({"error": "Assigned by is required"}), 400

    parsed_due_date = None
    if due_date:
        if not isinstance(due_date, str):
            return jsonify({"error": "Due date must be a valid ISO format string"}), 400
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
def permanent_delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 400
    
    db.session.delete(task)
    db.session.commit()

    return jsonify({"message": "Task permanently deleted"}), 200