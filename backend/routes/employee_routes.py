from flask import Blueprint, jsonify
from models.employee import Employee

employee_bp = Blueprint(
    "employee_bp",
    __name__,
    url_prefix="/api/employees"
)


@employee_bp.route("/", methods=["GET"])
def get_employees():
    employees = Employee.query.all()

    result = []

    for employee in employees:
        result.append({
            "id": employee.id,
            "name": employee.name,
            "email": employee.email,
            "role": employee.role,
            "department": employee.department,
            "experience_years": float(employee.experience_years)
            if employee.experience_years is not None else None,
            "weekly_capacity_hours": float(
                employee.weekly_capacity_hours
            )
            if employee.weekly_capacity_hours is not None else None,
            "availability_status": employee.availability_status
        })

    return jsonify(result)