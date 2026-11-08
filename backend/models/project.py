from extensions import db
from sqlalchemy.dialects.postgresql import UUID


class Project(db.Model):
    __tablename__ = "managed_projects"

    id = db.Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=db.text("gen_random_uuid()")
    )

    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    start_date = db.Column(db.Date)
    deadline = db.Column(db.Date)

    priority = db.Column(
        db.String(20),
        nullable=False,
        default="Medium"
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="Planning"
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now()
    )