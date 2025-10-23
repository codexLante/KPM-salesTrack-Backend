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
    status = data.get("status")
    created_at = data.get("created_at", datetime.utcnow().isoformat())

    if not title:
        return jsonify({"error": "Title is required"}), 400
    if not description:
        return jsonify({"error": "Description is required"}), 400
    if not assigned_to:
        return jsonify({"error": "Assigned to is required"}), 400
    if not assigned_by:
        return jsonify({"error": "Assigned by is required"}), 400
    if not isinstance(due_date, str) or (due_date and not datetime.fromisoformat(due_date)):
        return jsonify({"error": "Due date must be a valid ISO format string"}), 400
    
    new_task = Task(
        title=title,
        description=description,
        due_date=datetime.fromisoformat(due_date) if due_date else None,
        assigned_to=assigned_to,
        assigned_by=assigned_by,
        status="pending",  # Default status
        created_at=datetime.utcnow()
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

@tasks_bp.route("/update/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()
    
    # Only get non-deleted tasks
    task = Task.query.filter_by(id=task_id, deleted_at=None).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    title = data.get("title", task.title)
    description = data.get("description", task.description)
    due_date = data.get("due_date", task.due_date.isoformat() if task.due_date else None)
    assigned_to = data.get("assigned_to", task.assigned_to)
    assigned_by = data.get("assigned_by", task.assigned_by)
    status = data.get("status", task.status)

    if not title:
        return jsonify({"error": "Title is required"}), 400
    if not description:
        return jsonify({"error": "Description is required"}), 400
    if not assigned_to:
        return jsonify({"error": "Assigned to is required"}), 400
    if not assigned_by:
        return jsonify({"error": "Assigned by is required"}), 400
    if not isinstance(due_date, str) or (due_date and not datetime.fromisoformat(due_date)):
        return jsonify({"error": "Due date must be a valid ISO format string"}), 400

    task.title = title
    task.description = description
    task.due_date = datetime.fromisoformat(due_date) if due_date else None
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

# Soft delete - marks task as deleted instead of removing it
@tasks_bp.route("/delete/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    # Only get non-deleted tasks
    task = Task.query.filter_by(id=task_id, deleted_at=None).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    # Soft delete by setting deleted_at timestamp
    task.deleted_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"message": "Task deleted successfully"}), 200

# Get all active (non-deleted) tasks
@tasks_bp.route("/", methods=["GET"])
def get_tasks():
    tasks = Task.query.filter_by(deleted_at=None).all()
    
    return jsonify({
        "tasks": [{
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "assigned_to": task.assigned_to,
            "assigned_by": task.assigned_by,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "created_at": task.created_at.isoformat()
        } for task in tasks]
    }), 200

# Get single task
@tasks_bp.route("/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = Task.query.filter_by(id=task_id, deleted_at=None).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    return jsonify({
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

# Restore a deleted task
@tasks_bp.route("/restore/<int:task_id>", methods=["PATCH"])
def restore_task(task_id):
    # Get only deleted tasks
    task = Task.query.filter(Task.id == task_id, Task.deleted_at.isnot(None)).first()
    if not task:
        return jsonify({"error": "Deleted task not found"}), 404
    
    # Restore by clearing deleted_at
    task.deleted_at = None
    db.session.commit()

    return jsonify({"message": "Task restored successfully"}), 200

# Get deleted tasks (trash)
@tasks_bp.route("/trash", methods=["GET"])
def get_deleted_tasks():
    tasks = Task.query.filter(Task.deleted_at.isnot(None)).all()
    
    return jsonify({
        "tasks": [{
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "assigned_to": task.assigned_to,
            "assigned_by": task.assigned_by,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "created_at": task.created_at.isoformat(),
            "deleted_at": task.deleted_at.isoformat()
        } for task in tasks]
    }), 200

# Permanently delete a task (hard delete)
@tasks_bp.route("/permanent/<int:task_id>", methods=["DELETE"])
def permanent_delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    db.session.delete(task)
    db.session.commit()

    return jsonify({"message": "Task permanently deleted"}), 200