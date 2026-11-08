
from extensions import db
from sqlalchemy.dialects.postgresql import UUID


class Employee(db.Model):
    """
    Maps to the existing historical employees table.
    """

    __tablename__ = "employees"

    id = db.Column(
        UUID(as_uuid=False),
        primary_key=True
    )

    created_at = db.Column(
        db.DateTime(timezone=True)
    )

    team_id = db.Column(
        UUID(as_uuid=False),
        nullable=True
    )
