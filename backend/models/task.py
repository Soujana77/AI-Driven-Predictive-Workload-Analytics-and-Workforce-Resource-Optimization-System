from extensions import db
from sqlalchemy.dialects.postgresql import UUID


class Task(db.Model):
    __tablename__ = "managed_tasks"

    id = db.Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=db.text("gen_random_uuid()")
    )

    project_id = db.Column(
        UUID(as_uuid=False),
        db.ForeignKey("managed_projects.id", ondelete="CASCADE"),
        nullable=False
    )

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    assigned_employee_id = db.Column(
        UUID(as_uuid=False),
        db.ForeignKey(
            "employee_profiles.employee_id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    estimated_hours = db.Column(
        db.Numeric(7, 2),
        default=0
    )

    due_date = db.Column(db.Date)

    priority = db.Column(
        db.String(20),
        nullable=False,
        default="Medium"
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="To Do"
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now()
    )