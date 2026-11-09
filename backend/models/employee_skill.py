
from extensions import db
from sqlalchemy.dialects.postgresql import UUID


class EmployeeSkill(db.Model):

    __tablename__ = "employee_skills"

    employee_id = db.Column(
        UUID(as_uuid=False),
        db.ForeignKey(
            "employee_profiles.employee_id",
            ondelete="CASCADE"
        ),
        primary_key=True
    )

    skill_id = db.Column(
        UUID(as_uuid=False),
        db.ForeignKey(
            "skills.id",
            ondelete="CASCADE"
        ),
        primary_key=True
    )

    proficiency_level = db.Column(
        db.String(20),
        nullable=False
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
