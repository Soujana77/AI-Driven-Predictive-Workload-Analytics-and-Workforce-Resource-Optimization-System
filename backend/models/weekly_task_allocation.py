
from extensions import db
from sqlalchemy.dialects.postgresql import UUID


class WeeklyTaskAllocation(db.Model):
    __tablename__ = "weekly_task_allocations"

    id = db.Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=db.text("gen_random_uuid()")
    )

    task_id = db.Column(
        UUID(as_uuid=False),
        db.ForeignKey("managed_tasks.id", ondelete="CASCADE"),
        nullable=False
    )

    employee_id = db.Column(
        UUID(as_uuid=False),
        db.ForeignKey(
            "employee_profiles.employee_id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    week_start = db.Column(
        db.Date,
        nullable=False
    )

    allocated_hours = db.Column(
        db.Numeric(7, 2),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        onupdate=db.func.now(),
        nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint(
            "task_id",
            "employee_id",
            "week_start",
            name="uq_task_employee_week"
        ),
        db.CheckConstraint(
            "allocated_hours > 0",
            name="chk_allocated_hours_positive"
        ),
        db.Index(
            "idx_weekly_allocations_employee_week",
            "employee_id",
            "week_start"
        ),
        db.Index(
            "idx_weekly_allocations_task",
            "task_id"
        )
    )
