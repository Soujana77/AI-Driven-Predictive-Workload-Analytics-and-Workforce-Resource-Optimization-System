
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from extensions import db
from models.skill import Skill


skill_bp = Blueprint(
    "skill_bp",
    __name__,
    url_prefix="/api/skills"
)


def serialize_skill(skill):
    return {
        "id": skill.id,
        "name": skill.name,
        "description": skill.description,
        "created_at": (
            skill.created_at.isoformat()
            if skill.created_at else None
        )
    }


# GET: Retrieve all company skills
@skill_bp.route("/", methods=["GET"])
def get_skills():

    skills = Skill.query.order_by(Skill.name).all()

    return jsonify({
        "status": "success",
        "count": len(skills),
        "skills": [
            serialize_skill(skill) for skill in skills
        ]
    }), 200


# POST: Create a new company skill
@skill_bp.route("/", methods=["POST"])
def create_skill():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "Request body must be a JSON object"
        }), 400

    unknown_fields = set(data.keys()) - {"name", "description"}

    if unknown_fields:
        return jsonify({
            "status": "error",
            "message": "Unknown fields provided",
            "fields": sorted(unknown_fields)
        }), 400

    name = data.get("name")

    if not isinstance(name, str) or not name.strip():
        return jsonify({
            "status": "error",
            "message": "A valid skill name is required"
        }), 400

    name = name.strip()

    if len(name) > 100:
        return jsonify({
            "status": "error",
            "message": "Skill name cannot exceed 100 characters"
        }), 400

    description = data.get("description")

    if description is not None:
        if not isinstance(description, str):
            return jsonify({
                "status": "error",
                "message": "Description must be a string"
            }), 400

        description = description.strip() or None

    # Check duplicate names without considering letter case.
    existing = Skill.query.filter(
        db.func.lower(Skill.name) == name.lower()
    ).first()

    if existing:
        return jsonify({
            "status": "error",
            "message": "This skill already exists"
        }), 409

    skill = Skill(
        name=name,
        description=description
    )

    try:
        db.session.add(skill)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": "This skill already exists"
        }), 409

    return jsonify({
        "status": "success",
        "message": "Skill created successfully",
        "skill": serialize_skill(skill)
    }), 201


# GET: Retrieve an individual skill
@skill_bp.route("/<string:skill_id>", methods=["GET"])
def get_skill_by_id(skill_id):

    from uuid import UUID

    try:
        UUID(skill_id)
    except (ValueError, TypeError, AttributeError):
        return jsonify({
            "status": "error",
            "message": "Invalid skill ID format"
        }), 400

    skill = db.session.get(Skill, skill_id)

    if not skill:
        return jsonify({
            "status": "error",
            "message": "Skill not found"
        }), 404

    return jsonify({
        "status": "success",
        "skill": serialize_skill(skill)
    }), 200
