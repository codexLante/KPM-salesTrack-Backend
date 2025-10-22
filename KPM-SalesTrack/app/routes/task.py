from flask import Blueprint, jsonify, request
from app.models import Task
from app.db import db
from datetime import datetime

tasks_bp = Blueprint("tasks", __name__)

@tasks_bp.route("/add", methods=["POST"])
def add_task():
    data = request.get_json()
    user_id = data.get("user_id")

    title = data.get("title")
    description = data.get("description")
    due_date = data.get("due_date")

    if not title:
        return jsonify({"error": "Title is required"}), 400

    new_task = Task(
        title=title,
        description=description,
        user_id=user_id,
        due_date=datetime.fromisoformat(due_date) if due_date else None
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
            "due_date": new_task.due_date.isoformat() if new_task.due_date else None,
            "created_at": new_task.created_at.isoformat()
        }
    }), 201

@tasks_bp.route("/all", methods=["GET"])
def get_tasks():
    user_id = request.json.get("user_id")
    tasks = Task.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        "tasks": [{
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "created_at": task.created_at.isoformat()
        } for task in tasks]
    }), 200

@tasks_bp.route("/<int:task_id>/status", methods=["PUT"])
def update_task_status():
    data = request.get_json()
    user_id = data.get("user_id")
    task_id = data.get("task_id")
    status = data.get("status")

    task = Task.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    task.status = status
    db.session.commit()
    
    return jsonify({"message": "Task status updated"}), 200