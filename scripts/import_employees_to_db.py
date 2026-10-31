import os
import sys

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.append(PROJECT_ROOT)

load_dotenv(
    os.path.join(PROJECT_ROOT, "backend", ".env")
)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL not found in backend/.env"
    )


USERS_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "raw",
    "users.csv"
)


print("Loading users dataset...")

users = pd.read_csv(USERS_FILE)

print(f"Users loaded: {len(users):,}")


# Convert dataset fields to our employee structure

employees = pd.DataFrame({
    "id": users["id"],
    "name": "Unknown",
    "email": None,
    "role": "Employee",
    "department": None,
    "experience_years": None,
    "weekly_capacity_hours": 40,
    "availability_status": "Available",
})


print("\nEmployee records prepared:")
print(employees.head())


print("\nConnecting to PostgreSQL...")

engine = create_engine(DATABASE_URL)

with engine.begin() as connection:

    employees.to_sql(
        "employees",
        connection,
        if_exists="append",
        index=False
    )

print("\nEmployees imported successfully!")
print(f"Records inserted: {len(employees):,}")