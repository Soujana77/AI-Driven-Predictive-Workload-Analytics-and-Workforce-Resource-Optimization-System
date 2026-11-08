from flask import Blueprint, jsonify, request
from datetime import date

from extensions import db
from models.task import Task
from models.project import Project
from models.employee_profile import EmployeeProfile

task_bp = Blueprint(
    "task_bp",
    __name__,
    url_prefix="/api/tasks"
)


@task_bp.route("/", methods=["GET"])
def get_tasks():
    tasks = Task.query.order_by(
        Task.created_at.desc()
    ).all()

    result = []

    for task in tasks:
        result.append({
            "id": task.id,
            "project_id": task.project_id,
            "title": task.title,
            "description": task.description,
            "assigned_employee_id": task.assigned_employee_id,
            "estimated_hours": float(task.estimated_hours or 0),
            "due_date": (
                task.due_date.isoformat()
                if task.due_date else None
            ),
            "priority": task.priority,
            "status": task.status
        })

    return jsonify({
        "status": "success",
        "count": len(result),
        "tasks": result
    }), 200


@task_bp.route("/", methods=["POST"])
def create_task():
    data = request.get_json(silent=True) or {}

    if not data.get("project_id") or not data.get("title"):
        return jsonify({
            "status": "error",
            "message": "Project ID and task title are required"
        }), 400

    project = db.session.get(Project, data["project_id"])

    if not project:
        return jsonify({
            "status": "error",
            "message": "Project not found"
        }), 404

    employee_id = data.get("assigned_employee_id")

    if employee_id:
        employee = db.session.get(EmployeeProfile, employee_id)

        if not employee:
            return jsonify({
                "status": "error",
                "message": "Employee profile not found"
            }), 404

    try:
        estimated_hours = float(
            data.get("estimated_hours", 0)
        )

        if estimated_hours < 0:
            raise ValueError()

        task = Task(
            project_id=data["project_id"],
            title=data["title"],
            description=data.get("description"),
            assigned_employee_id=employee_id,
            estimated_hours=estimated_hours,
            due_date=(
                date.fromisoformat(data["due_date"])
                if data.get("due_date") else None
            ),
            priority=data.get("priority", "Medium"),
            status=data.get("status", "To Do")
        )

        db.session.add(task)
        db.session.commit()

    except ValueError:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": "Invalid date or estimated hours"
        }), 400

    return jsonify({
        "status": "success",
        "message": "Task created successfully",
        "task_id": task.id
    }), 201