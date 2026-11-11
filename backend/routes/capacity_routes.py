
from flask import Blueprint, jsonify, request
from datetime import date
from decimal import Decimal, InvalidOperation
from uuid import UUID

from extensions import db
from models.employee_profile import EmployeeProfile
from models.weekly_task_allocation import WeeklyTaskAllocation
from models.task import Task

from services.capacity_service import (
    get_employee_weekly_capacity
)


capacity_bp = Blueprint(
    "capacity_bp",
    __name__,
    url_prefix="/api/capacity"
)


def valid_uuid(value):
    try:
        UUID(str(value))
        return True
    except (ValueError, TypeError, AttributeError):
        return False


# --------------------------------------------------
# GET: Retrieve employee weekly capacity
# --------------------------------------------------

@capacity_bp.route("/<string:employee_id>", methods=["GET"])
def get_employee_capacity(employee_id):

    if not valid_uuid(employee_id):
        return jsonify({
            "status": "error",
            "message": "Invalid employee ID"
        }), 400

    week_value = request.args.get("week_start")

    if not week_value:
        return jsonify({
            "status": "error",
            "message": "week_start is required (YYYY-MM-DD)"
        }), 400

    try:
        week_start = date.fromisoformat(week_value)
    except ValueError:
        return jsonify({
            "status": "error",
            "message": "Invalid week_start date"
        }), 400

    if week_start.weekday() != 0:
        return jsonify({
            "status": "error",
            "message": "week_start must be a Monday"
        }), 400

    result, error = get_employee_weekly_capacity(
        employee_id,
        week_start
    )

    if error:
        return jsonify({
            "status": "error",
            "message": error
        }), 404

    return jsonify({
        "status": "success",
        "capacity": result
    }), 200


# --------------------------------------------------
# POST: Allocate task hours to an employee and week
# --------------------------------------------------

@capacity_bp.route("/allocations", methods=["POST"])
def create_weekly_allocation():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "Request body must be a JSON object"
        }), 400

    required_fields = [
        "task_id",
        "employee_id",
        "week_start",
        "allocated_hours"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "status": "error",
                "message": f"{field} is required"
            }), 400

    task_id = data["task_id"]
    employee_id = data["employee_id"]

    if not valid_uuid(task_id) or not valid_uuid(employee_id):
        return jsonify({
            "status": "error",
            "message": "Invalid task ID or employee ID"
        }), 400

    try:
        week_start = date.fromisoformat(data["week_start"])
    except (ValueError, TypeError):
        return jsonify({
            "status": "error",
            "message": "Invalid week_start date"
        }), 400

    if week_start.weekday() != 0:
        return jsonify({
            "status": "error",
            "message": "week_start must be a Monday"
        }), 400

    try:
        allocated_hours = Decimal(
            str(data["allocated_hours"])
        )

        if not allocated_hours.is_finite() or allocated_hours <= 0:
            raise InvalidOperation

    except (InvalidOperation, ValueError, TypeError):
        return jsonify({
            "status": "error",
            "message": "allocated_hours must be a positive number"
        }), 400

    employee = db.session.get(EmployeeProfile, employee_id)
    task = db.session.get(Task, task_id)

    if not employee:
        return jsonify({
            "status": "error",
            "message": "Employee profile not found"
        }), 404

    if not task:
        return jsonify({
            "status": "error",
            "message": "Task not found"
        }), 404

    if task.status == "Completed":
        return jsonify({
            "status": "error",
            "message": "Cannot allocate hours to a completed task"
        }), 400

    if task.assigned_employee_id != employee_id:
        return jsonify({
            "status": "error",
            "message": "Task is not assigned to this employee"
        }), 400

    if employee.availability_status != "Available":
        return jsonify({
            "status": "error",
            "message": "Employee is not currently available"
        }), 400

    existing_allocation = WeeklyTaskAllocation.query.filter_by(
        task_id=task_id,
        employee_id=employee_id,
        week_start=week_start
    ).first()

    if existing_allocation:
        return jsonify({
            "status": "error",
            "message": "Allocation already exists for this task, employee and week"
        }), 409

    existing_task_hours = (
        db.session.query(
            db.func.coalesce(
                db.func.sum(WeeklyTaskAllocation.allocated_hours),
                0
            )
        )
        .filter(WeeklyTaskAllocation.task_id == task_id)
        .scalar()
    )

    if (
        Decimal(str(existing_task_hours)) + allocated_hours
        > Decimal(str(task.estimated_hours or 0))
    ):
        return jsonify({
            "status": "error",
            "message": "Total allocations cannot exceed estimated task hours"
        }), 400

    capacity, error = get_employee_weekly_capacity(
        employee_id,
        week_start
    )

    if error:
        return jsonify({
            "status": "error",
            "message": error
        }), 404

    if allocated_hours > Decimal(
        str(capacity["remaining_capacity_hours"])
    ):
        return jsonify({
            "status": "error",
            "message": "Allocation exceeds employee's remaining weekly capacity",
            "remaining_capacity_hours": capacity[
                "remaining_capacity_hours"
            ]
        }), 400

    allocation = WeeklyTaskAllocation(
        task_id=task_id,
        employee_id=employee_id,
        week_start=week_start,
        allocated_hours=allocated_hours
    )

    try:
        db.session.add(allocation)
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return jsonify({
        "status": "success",
        "message": "Weekly task allocation created successfully",
        "allocation": {
            "id": allocation.id,
            "task_id": allocation.task_id,
            "employee_id": allocation.employee_id,
            "week_start": allocation.week_start.isoformat(),
            "allocated_hours": float(allocation.allocated_hours)
        }
    }), 201
