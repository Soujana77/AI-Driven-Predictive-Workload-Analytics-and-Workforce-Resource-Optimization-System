from flask import Blueprint, jsonify, request
from datetime import date

from extensions import db
from models.project import Project

project_bp = Blueprint(
    "project_bp",
    __name__,
    url_prefix="/api/projects"
)


@project_bp.route("/", methods=["GET"])
def get_projects():
    projects = Project.query.order_by(
        Project.created_at.desc()
    ).all()

    result = []

    for project in projects:
        result.append({
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "start_date": (
                project.start_date.isoformat()
                if project.start_date else None
            ),
            "deadline": (
                project.deadline.isoformat()
                if project.deadline else None
            ),
            "priority": project.priority,
            "status": project.status
        })

    return jsonify({
        "status": "success",
        "count": len(result),
        "projects": result
    }), 200


@project_bp.route("/", methods=["POST"])
def create_project():
    data = request.get_json(silent=True) or {}

    if not data.get("name"):
        return jsonify({
            "status": "error",
            "message": "Project name is required"
        }), 400

    try:
        project = Project(
            name=data["name"],
            description=data.get("description"),
            start_date=(
                date.fromisoformat(data["start_date"])
                if data.get("start_date") else None
            ),
            deadline=(
                date.fromisoformat(data["deadline"])
                if data.get("deadline") else None
            ),
            priority=data.get("priority", "Medium"),
            status=data.get("status", "Planning")
        )

        db.session.add(project)
        db.session.commit()

    except ValueError:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": "Invalid date format. Use YYYY-MM-DD."
        }), 400

    return jsonify({
        "status": "success",
        "message": "Project created successfully",
        "project_id": project.id
    }), 201