
from sqlalchemy import func

from extensions import db
from models.employee_profile import EmployeeProfile
from models.weekly_task_allocation import WeeklyTaskAllocation
from models.task import Task


def get_employee_weekly_capacity(employee_id, week_start):

    employee = db.session.get(EmployeeProfile, employee_id)

    if not employee:
        return None, "Employee profile not found"

    allocated_hours = (
        db.session.query(
            func.coalesce(
                func.sum(WeeklyTaskAllocation.allocated_hours),
                0
            )
        )
        .join(
            Task,
            Task.id == WeeklyTaskAllocation.task_id
        )
        .filter(
            WeeklyTaskAllocation.employee_id == employee_id,
            WeeklyTaskAllocation.week_start == week_start,
            Task.status != "Completed"
        )
        .scalar()
    )

    weekly_capacity = float(employee.weekly_capacity_hours)
    allocated_hours = float(allocated_hours)

    remaining_capacity = weekly_capacity - allocated_hours

    return {
        "employee_id": employee.employee_id,
        "employee_name": employee.full_name,
        "week_start": week_start.isoformat(),
        "availability_status": employee.availability_status,
        "weekly_capacity_hours": weekly_capacity,
        "allocated_hours": allocated_hours,
        "remaining_capacity_hours": round(
            remaining_capacity, 2
        ),
        "is_overloaded": remaining_capacity < 0
    }, None
