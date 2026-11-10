
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from uuid import UUID

from extensions import db
from models.employee_profile import EmployeeProfile
from models.skill import Skill
from models.employee_skill import EmployeeSkill


employee_skill_bp = Blueprint(
    "employee_skill_bp",
    __name__,
    url_prefix="/api/employee-skills"
)


VALID_PROFICIENCY_LEVELS = {
    "Beginner",
    "Intermediate",
    "Advanced",
    "Expert"
}


def valid_uuid(value):
    try:
        UUID(value)
        return True
    except (ValueError, TypeError, AttributeError):
        return False


# POST: Assign a skill to an employee
@employee_skill_bp.route("/", methods=["POST"])
def assign_skill():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "Request body must be a JSON object"
        }), 400

    allowed_fields = {
        "employee_id",
        "skill_id",
        "proficiency_level"
    }

    if set(data.keys()) - allowed_fields:
        return jsonify({
            "status": "error",
            "message": "Unknown fields provided"
        }), 400

    employee_id = data.get("employee_id")
    skill_id = data.get("skill_id")
    proficiency = data.get("proficiency_level")

    if not employee_id or not skill_id or not proficiency:
        return jsonify({
            "status": "error",
            "message": "employee_id, skill_id and proficiency_level are required"
        }), 400

    if not isinstance(employee_id, str) or not valid_uuid(employee_id):
        return jsonify({
            "status": "error",
            "message": "Invalid employee ID format"
        }), 400

    if not isinstance(skill_id, str) or not valid_uuid(skill_id):
        return jsonify({
            "status": "error",
            "message": "Invalid skill ID format"
        }), 400

    if not isinstance(proficiency, str):
        return jsonify({
            "status": "error",
            "message": "Invalid proficiency level"
        }), 400

    if proficiency not in VALID_PROFICIENCY_LEVELS:
        return jsonify({
            "status": "error",
            "message": "Proficiency must be Beginner, Intermediate, Advanced or Expert"
        }), 400

    employee = db.session.get(
        EmployeeProfile, employee_id
    )

    if not employee:
        return jsonify({
            "status": "error",
            "message": "Employee profile not found"
        }), 404

    skill = db.session.get(Skill, skill_id)

    if not skill:
        return jsonify({
            "status": "error",
            "message": "Skill not found"
        }), 404

    existing = db.session.get(
        EmployeeSkill,
        (employee_id, skill_id)
    )

    if existing:
        return jsonify({
            "status": "error",
            "message": "This skill is already assigned to the employee"
        }), 409

    assignment = EmployeeSkill(
        employee_id=employee_id,
        skill_id=skill_id,
        proficiency_level=proficiency
    )

    try:
        db.session.add(assignment)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": "Could not assign skill. Check for duplicate or invalid references."
        }), 409

    return jsonify({
        "status": "success",
        "message": "Skill assigned successfully",
        "employee_id": employee_id,
        "skill_id": skill_id,
        "proficiency_level": proficiency
    }), 201


# GET: Retrieve all skills of one employee
@employee_skill_bp.route(
    "/<string:employee_id>",
    methods=["GET"]
)
def get_employee_skills(employee_id):

    if not valid_uuid(employee_id):
        return jsonify({
            "status": "error",
            "message": "Invalid employee ID format"
        }), 400

    employee = db.session.get(
        EmployeeProfile, employee_id
    )

    if not employee:
        return jsonify({
            "status": "error",
            "message": "Employee profile not found"
        }), 404

    assignments = (
        db.session.query(EmployeeSkill, Skill)
        .join(Skill, EmployeeSkill.skill_id == Skill.id)
        .filter(EmployeeSkill.employee_id == employee_id)
        .order_by(Skill.name)
        .all()
    )

    result = []

    for assignment, skill in assignments:
        result.append({
            "skill_id": skill.id,
            "skill_name": skill.name,
            "description": skill.description,
            "proficiency_level": assignment.proficiency_level,
            "assigned_at": (
                assignment.created_at.isoformat()
                if assignment.created_at else None
            ),
            "updated_at": (
                assignment.updated_at.isoformat()
                if assignment.updated_at else None
            )
        })

    return jsonify({
        "status": "success",
        "employee_id": employee_id,
        "employee_name": employee.full_name,
        "count": len(result),
        "skills": result
    }), 200


# PATCH: Update employee skill proficiency
@employee_skill_bp.route(
    "/<string:employee_id>/<string:skill_id>",
    methods=["PATCH"]
)
def update_employee_skill(employee_id, skill_id):

    if not valid_uuid(employee_id) or not valid_uuid(skill_id):
        return jsonify({
            "status": "error",
            "message": "Invalid employee or skill ID format"
        }), 400

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "Request body must be a JSON object"
        }), 400

    if set(data.keys()) != {"proficiency_level"}:
        return jsonify({
            "status": "error",
            "message": "Only proficiency_level can be updated"
        }), 400

    proficiency = data.get("proficiency_level")

    if not isinstance(proficiency, str) or proficiency not in VALID_PROFICIENCY_LEVELS:
        return jsonify({
            "status": "error",
            "message": "Invalid proficiency level"
        }), 400

    assignment = db.session.get(
        EmployeeSkill,
        (employee_id, skill_id)
    )

    if not assignment:
        return jsonify({
            "status": "error",
            "message": "Employee skill assignment not found"
        }), 404

    assignment.proficiency_level = proficiency

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Employee skill proficiency updated",
        "employee_id": employee_id,
        "skill_id": skill_id,
        "proficiency_level": proficiency
    }), 200


# DELETE: Remove a skill from an employee
@employee_skill_bp.route(
    "/<string:employee_id>/<string:skill_id>",
    methods=["DELETE"]
)
def remove_employee_skill(employee_id, skill_id):

    if not valid_uuid(employee_id) or not valid_uuid(skill_id):
        return jsonify({
            "status": "error",
            "message": "Invalid employee or skill ID format"
        }), 400

    assignment = db.session.get(
        EmployeeSkill,
        (employee_id, skill_id)
    )

    if not assignment:
        return jsonify({
            "status": "error",
            "message": "Employee skill assignment not found"
        }), 404

    db.session.delete(assignment)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Employee skill removed successfully"
    }), 200
