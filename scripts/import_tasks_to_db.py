import os
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine


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
# 3. Load tasks dataset
# --------------------------------------------------

TASKS_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "raw",
    "tasks.csv"
)

print("Loading tasks dataset...")

tasks = pd.read_csv(TASKS_FILE)

print(f"Tasks loaded: {len(tasks):,}")


# --------------------------------------------------
# 4. Select required columns
# --------------------------------------------------

tasks = tasks[
    [
        "id",
        "created_at",
        "is_container",
        "parent_id",
        "project_id"
    ]
].copy()


# --------------------------------------------------
# 5. Convert timestamp
# --------------------------------------------------

tasks["created_at"] = pd.to_datetime(
    tasks["created_at"],
    format="mixed",
    utc=True
)


# --------------------------------------------------
# 6. Convert boolean field
# --------------------------------------------------

tasks["is_container"] = (
    tasks["is_container"]
    .astype(str)
    .str.lower()
    .map({
        "true": True,
        "false": False,
        "1": True,
        "0": False
    })
)


# --------------------------------------------------
# 7. Prepare nullable parent IDs
# --------------------------------------------------

tasks["parent_id"] = tasks["parent_id"].where(
    tasks["parent_id"].notna(),
    None
)


# --------------------------------------------------
# 8. Display prepared data
# --------------------------------------------------

print("\nPrepared task records:")
print(tasks.head())


# --------------------------------------------------
# 9. Connect to PostgreSQL
# --------------------------------------------------

print("\nConnecting to PostgreSQL...")

engine = create_engine(DATABASE_URL)


# --------------------------------------------------
# 10. Insert tasks
# --------------------------------------------------

with engine.begin() as connection:

    tasks.to_sql(
        "tasks",
        connection,
        if_exists="append",
        index=False
    )


print("\nTasks imported successfully!")
print(f"Records inserted: {len(tasks):,}")