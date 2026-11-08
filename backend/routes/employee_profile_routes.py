from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from extensions import db
from models.employee import Employee
from models.employee_profile import EmployeeProfile

profile_bp = Blueprint(
    "profile_bp",
    __name__,
    url_prefix="/api/employee-profiles"
)


@profile_bp.route("/", methods=["GET"])
def get_profiles():
    profiles = EmployeeProfile.query.all()

    result = []

    for profile in profiles:
        result.append({
            "employee_id": profile.employee_id,
            "full_name": profile.full_name,
            "email": profile.email,
            "job_title": profile.job_title,
            "department": profile.department,
            "experience_years": (
                float(profile.experience_years)
                if profile.experience_years is not None else None
            ),
            "weekly_capacity_hours": float(
                profile.weekly_capacity_hours
            ),
            "availability_status": profile.availability_status
        })

    return jsonify({
        "status": "success",
        "count": len(result),
        "profiles": result
    }), 200


@profile_bp.route("/", methods=["POST"])
def create_profile():
    data = request.get_json(silent=True) or {}

    required_fields = ["employee_id", "full_name"]

    for field in required_fields:
        if not data.get(field):
            return jsonify({
                "status": "error",
                "message": f"{field} is required"
            }), 400

    employee = db.session.get(Employee, data["employee_id"])

    if not employee:
        return jsonify({
            "status": "error",
            "message": "Historical employee not found"
        }), 404

    profile = EmployeeProfile(
        employee_id=data["employee_id"],
        full_name=data["full_name"],
        email=data.get("email"),
        job_title=data.get("job_title"),
        department=data.get("department"),
        experience_years=data.get("experience_years"),
        weekly_capacity_hours=data.get(
            "weekly_capacity_hours", 40
        ),
        availability_status=data.get(
            "availability_status", "Available"
        )
    )

    try:
        db.session.add(profile)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": "Profile already exists or email is already registered"
        }), 409

    return jsonify({
        "status": "success",
        "message": "Employee profile created",
        "employee_id": profile.employee_id
    }), 201