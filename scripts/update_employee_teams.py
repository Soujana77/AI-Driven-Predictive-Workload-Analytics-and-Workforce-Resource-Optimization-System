import os
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# --------------------------------------------------
# 1. Find project root
# --------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


# --------------------------------------------------
# 2. Load database configuration
# --------------------------------------------------

load_dotenv(
    os.path.join(PROJECT_ROOT, "backend", ".env")
)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL not found in backend/.env"
    )


# --------------------------------------------------
# 3. Load users dataset
# --------------------------------------------------

USERS_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "raw",
    "users.csv"
)

print("Loading users dataset...")

users = pd.read_csv(USERS_FILE)

print(f"Users loaded: {len(users):,}")


# --------------------------------------------------
# 4. Keep only employee ID and team ID
# --------------------------------------------------

users = users[["id", "team_id"]].copy()

users = users.rename(
    columns={
        "id": "employee_id"
    }
)

print("\nEmployee-team mappings:")
print(users.head())


# --------------------------------------------------
# 5. Connect to PostgreSQL
# --------------------------------------------------

print("\nConnecting to PostgreSQL...")

engine = create_engine(DATABASE_URL)


# --------------------------------------------------
# 6. Update employees
# --------------------------------------------------

update_query = text("""
    UPDATE employees
    SET team_id = :team_id
    WHERE id = :employee_id
""")


records = users.to_dict("records")

with engine.begin() as connection:

    connection.execute(
        update_query,
        records
    )


print("\nEmployee-team relationships updated successfully!")
print(f"Records processed: {len(records):,}")