from extensions import db


class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True)
    role = db.Column(db.String(100))
    department = db.Column(db.String(100))
    experience_years = db.Column(db.Numeric(4, 1))
    weekly_capacity_hours = db.Column(
        db.Numeric(5, 2),
        default=40
    )
    availability_status = db.Column(
        db.String(50),
        default="Available"
    )
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )