
from extensions import db
from sqlalchemy.dialects.postgresql import UUID


class Skill(db.Model):

    __tablename__ = "skills"

    id = db.Column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=db.text("gen_random_uuid()")
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now()
    )
