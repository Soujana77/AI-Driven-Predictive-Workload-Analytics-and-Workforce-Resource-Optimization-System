
import os
import io
import csv
import pandas as pd
import psycopg2

from dotenv import load_dotenv


# ============================================================
# 1. PROJECT ROOT
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


# ============================================================
# 2. DATABASE CONFIGURATION
# ============================================================

load_dotenv(
    os.path.join(PROJECT_ROOT, "backend", ".env")
)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in backend/.env")


# ============================================================
# 3. DATASET PATH
# ============================================================

TASKS_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "raw",
    "tasks.csv"
)


# ============================================================
# 4. LOAD DATASET
# ============================================================

print("Loading tasks dataset...")

tasks = pd.read_csv(TASKS_FILE)

print(f"Tasks loaded: {len(tasks):,}")


# ============================================================
# 5. SELECT REQUIRED COLUMNS
# ============================================================

tasks = tasks[
    [
        "id",
        "created_at",
        "is_container",
        "parent_id",
        "project_id"
    ]
].copy()


# ============================================================
# 6. CONVERT TIMESTAMP
# ============================================================

print("\nConverting timestamps...")

tasks["created_at"] = pd.to_datetime(
    tasks["created_at"],
    format="mixed",
    utc=True
)


# ============================================================
# 7. CORRECT BOOLEAN CONVERSION
# ============================================================

print("\nConverting Boolean values...")

boolean_mapping = {
    "t": True,
    "f": False,
    "true": True,
    "false": False,
    "1": True,
    "0": False
}

tasks["is_container"] = (
    tasks["is_container"]
    .astype(str)
    .str.strip()
    .str.lower()
    .map(boolean_mapping)
)

invalid_booleans = tasks["is_container"].isna().sum()

if invalid_booleans > 0:
    raise ValueError(
        f"Found {invalid_booleans} invalid Boolean values."
    )

print("Boolean conversion successful!")

print(tasks["is_container"].value_counts())


# ============================================================
# 8. HANDLE NULL PARENT IDS
# ============================================================

tasks["parent_id"] = tasks["parent_id"].where(
    tasks["parent_id"].notna(),
    None
)


# ============================================================
# 9. PREPARE CSV DATA FOR POSTGRESQL COPY
# ============================================================

print("\nPreparing task records...")

tasks["created_at"] = (
    tasks["created_at"]
    .dt.strftime("%Y-%m-%d %H:%M:%S.%f%z")
)

buffer = io.StringIO()

writer = csv.writer(
    buffer,
    lineterminator="\n"
)

for row in tasks.itertuples(index=False, name=None):
    writer.writerow(row)

buffer.seek(0)


# ============================================================
# 10. CONNECT TO POSTGRESQL
# ============================================================

print("\nConnecting to PostgreSQL...")

connection = psycopg2.connect(DATABASE_URL)

cursor = connection.cursor()


# ============================================================
# 11. BULK IMPORT USING COPY
# ============================================================

print("\nImporting tasks using PostgreSQL COPY...")

try:

    cursor.copy_expert(
        """
        COPY tasks (
            id,
            created_at,
            is_container,
            parent_id,
            project_id
        )
        FROM STDIN
        WITH (
            FORMAT CSV,
            NULL ''
        )
        """,
        buffer
    )

    connection.commit()

    print("\nTasks imported successfully!")
    print(f"Records inserted: {len(tasks):,}")

except Exception as error:

    connection.rollback()

    print("\nTask import failed!")
    print(error)

    raise

finally:

    cursor.close()
    connection.close()
