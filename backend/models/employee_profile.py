from extensions import db
from sqlalchemy.dialects.postgresql import UUID


class EmployeeProfile(db.Model):
    __tablename__ = "employee_profiles"

    employee_id = db.Column(
        UUID(as_uuid=False),
        db.ForeignKey("employees.id", ondelete="CASCADE"),
        primary_key=True
    )

    full_name = db.Column(
        db.String(150),
        nullable=False
    )

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=True
    )

    job_title = db.Column(db.String(100))
    department = db.Column(db.String(100))

    experience_years = db.Column(
        db.Numeric(4, 1)
    )

    weekly_capacity_hours = db.Column(
        db.Numeric(5, 2),
        nullable=False,
        default=40
    )

    availability_status = db.Column(
        db.String(30),
        nullable=False,
        default="Available"
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now()
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        onupdate=db.func.now()
    )