
from flask import Blueprint, jsonify
from models.employee import Employee

employee_bp = Blueprint(
    "employee_bp",
    __name__,
    url_prefix="/api/employees"
)


@employee_bp.route("/", methods=["GET"])
def get_employees():

    employees = Employee.query.limit(100).all()

    result = []

    for employee in employees:
        result.append({
            "id": employee.id,
            "team_id": employee.team_id,
            "created_at": (
                employee.created_at.isoformat()
                if employee.created_at else None
            )
        })

    return jsonify({
        "status": "success",
        "count": len(result),
        "employees": result
    })
