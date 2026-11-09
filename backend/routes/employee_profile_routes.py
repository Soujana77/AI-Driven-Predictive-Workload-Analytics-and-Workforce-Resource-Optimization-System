
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from decimal import Decimal, InvalidOperation
from uuid import UUID

from extensions import db
from models.employee import Employee
from models.employee_profile import EmployeeProfile


profile_bp = Blueprint(
    "profile_bp",
    __name__,
    url_prefix="/api/employee-profiles"
)


# --------------------------------------------------
# HELPER 1: Convert profile into JSON-compatible data
# --------------------------------------------------

def serialize_profile(profile):
    return {
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
        "availability_status": profile.availability_status,
        "created_at": (
            profile.created_at.isoformat()
            if profile.created_at else None
        ),
        "updated_at": (
            profile.updated_at.isoformat()
            if profile.updated_at else None
        )
    }


# --------------------------------------------------
# HELPER 2: Validate employee UUID
# --------------------------------------------------

def valid_uuid(employee_id):
    try:
        UUID(employee_id)
        return True
    except (ValueError, TypeError, AttributeError):
        return False


# --------------------------------------------------
# HELPER 3: Validate incoming profile information
# --------------------------------------------------

def validate_profile_data(data, partial=False):

    allowed_fields = {
        "full_name",
        "email",
        "job_title",
        "department",
        "experience_years",
        "weekly_capacity_hours",
        "availability_status"
    }

    unknown_fields = set(data.keys()) - allowed_fields

    if unknown_fields:
        return None, {
            "message": "Unknown fields provided",
            "fields": sorted(unknown_fields)
        }

    if not partial and not data.get("full_name"):
        return None, {"message": "full_name is required"}

    validated = {}

    string_limits = {
        "full_name": 150,
        "email": 255,
        "job_title": 100,
        "department": 100,
        "availability_status": 30
    }

    for field, maximum in string_limits.items():

        if field not in data:
            continue

        value = data[field]

        if value is None and field != "full_name":
            validated[field] = None
            continue

        if not isinstance(value, str):
            return None, {
                "message": f"{field} must be a string"
            }

        value = value.strip()

        if not value and field == "full_name":
            return None, {
                "message": "full_name cannot be empty"
            }

        if not value and field != "full_name":
            validated[field] = None
            continue

        if len(value) > maximum:
            return None, {
                "message": f"{field} cannot exceed {maximum} characters"
            }

        validated[field] = value

    numeric_limits = {
        "experience_years": Decimal("999.9"),
        "weekly_capacity_hours": Decimal("999.99")
    }

    for field, maximum in numeric_limits.items():

        if field not in data:
            continue

        value = data[field]

        if value is None and field == "experience_years":
            validated[field] = None
            continue

        if isinstance(value, bool):
            return None, {
                "message": f"{field} must be a valid number"
            }

        try:
            number = Decimal(str(value))

            if not number.is_finite():
                raise InvalidOperation

        except (InvalidOperation, ValueError, TypeError):
            return None, {
                "message": f"{field} must be a valid number"
            }

        if number < 0 or number > maximum:
            return None, {
                "message": f"{field} must be between 0 and {maximum}"
            }

        validated[field] = number

    return validated, None


# --------------------------------------------------
# GET: Retrieve all employee profiles
# --------------------------------------------------

@profile_bp.route("/", methods=["GET"])
def get_profiles():

    profiles = EmployeeProfile.query.all()

    result = [
        serialize_profile(profile)
        for profile in profiles
    ]

    return jsonify({
        "status": "success",
        "count": len(result),
        "profiles": result
    }), 200


# --------------------------------------------------
# POST: Create employee profile
# --------------------------------------------------

@profile_bp.route("/", methods=["POST"])
def create_profile():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "Request body must be a JSON object"
        }), 400

    required_fields = ["employee_id", "full_name"]

    for field in required_fields:
        if not data.get(field):
            return jsonify({
                "status": "error",
                "message": f"{field} is required"
            }), 400

    employee = db.session.get(
        Employee,
        data["employee_id"]
    )

    if not employee:
        return jsonify({
            "status": "error",
            "message": "Historical employee not found"
        }), 404

    validated, error = validate_profile_data({
        key: value
        for key, value in data.items()
        if key != "employee_id"
    })

    if error:
        return jsonify({
            "status": "error",
            **error
        }), 400

    profile = EmployeeProfile(
        employee_id=data["employee_id"],
        **validated
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


# --------------------------------------------------
# GET: Retrieve one employee profile by ID
# --------------------------------------------------

@profile_bp.route("/<string:employee_id>", methods=["GET"])
def get_profile_by_id(employee_id):

    if not valid_uuid(employee_id):
        return jsonify({
            "status": "error",
            "message": "Invalid employee ID format"
        }), 400

    profile = db.session.get(
        EmployeeProfile,
        employee_id
    )

    if not profile:
        return jsonify({
            "status": "error",
            "message": "Employee profile not found"
        }), 404

    return jsonify({
        "status": "success",
        "profile": serialize_profile(profile)
    }), 200


# --------------------------------------------------
# PUT / PATCH: Update employee profile
# --------------------------------------------------

@profile_bp.route(
    "/<string:employee_id>",
    methods=["PUT", "PATCH"]
)
def update_profile(employee_id):

    if not valid_uuid(employee_id):
        return jsonify({
            "status": "error",
            "message": "Invalid employee ID format"
        }), 400

    profile = db.session.get(
        EmployeeProfile,
        employee_id
    )

    if not profile:
        return jsonify({
            "status": "error",
            "message": "Employee profile not found"
        }), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({
            "status": "error",
            "message": "A non-empty JSON object is required"
        }), 400

    is_partial = request.method == "PATCH"

    if not is_partial:
        # PUT replaces the editable profile details.
        replacement_data = {
            "full_name": data.get("full_name"),
            "email": data.get("email"),
            "job_title": data.get("job_title"),
            "department": data.get("department"),
            "experience_years": data.get("experience_years"),
            "weekly_capacity_hours": data.get(
                "weekly_capacity_hours", 40
            ),
            "availability_status": data.get(
                "availability_status", "Available"
            )
        }
        data = replacement_data

    validated, error = validate_profile_data(
        data,
        partial=is_partial
    )

    if error:
        return jsonify({
            "status": "error",
            **error
        }), 400

    for field, value in validated.items():
        setattr(profile, field, value)

    try:
        db.session.commit()

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": "Email is already registered"
        }), 409

    return jsonify({
        "status": "success",
        "message": "Employee profile updated successfully",
        "profile": serialize_profile(profile)
    }), 200
