
import os
import io
import csv

import pandas as pd
import psycopg2

from dotenv import load_dotenv


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


# ============================================================
# LOAD DATABASE CONFIGURATION
# ============================================================

load_dotenv(
    os.path.join(
        PROJECT_ROOT,
        "backend",
        ".env"
    )
)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL not found in backend/.env"
    )


# ============================================================
# DATASET PATH
# ============================================================

DECLARATIONS_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "raw",
    "declarations.csv"
)


# ============================================================
# LOAD DATASET
# ============================================================

print("Loading declarations dataset...")

declarations = pd.read_csv(
    DECLARATIONS_FILE
)

print(
    f"Declarations loaded: {len(declarations):,}"
)


# ============================================================
# SELECT REQUIRED COLUMNS
# ============================================================

declarations = declarations[
    [
        "id",
        "created_at",
        "date",
        "duration",
        "source",
        "user_id",
        "task_id"
    ]
].copy()


# ============================================================
# CONVERT DATES
# ============================================================

print("\nConverting dates...")

declarations["created_at"] = pd.to_datetime(
    declarations["created_at"],
    format="mixed",
    utc=True
)

declarations["date"] = pd.to_datetime(
    declarations["date"],
    errors="coerce"
).dt.date


# ============================================================
# REMOVE INVALID DATES
# ============================================================

invalid_dates = declarations["date"].isna().sum()

print(f"Invalid dates found: {invalid_dates:,}")

declarations = declarations.dropna(
    subset=["date"]
).copy()

print(
    f"Valid records remaining: {len(declarations):,}"
)


# ============================================================
# PREPARE VALUES FOR POSTGRESQL
# ============================================================

print("\nPreparing database import...")

if declarations["created_at"].isna().any():
    raise ValueError("Invalid created_at values found.")

if declarations["duration"].isna().any():
    raise ValueError("Missing duration values found.")

declarations["created_at"] = (
    declarations["created_at"]
    .dt.strftime("%Y-%m-%d %H:%M:%S.%f%z")
)

declarations["date"] = declarations["date"].astype(str)

declarations["duration"] = (
    declarations["duration"].astype("int64")
)


# ============================================================
# CONNECT TO POSTGRESQL
# ============================================================

print("\nConnecting to PostgreSQL...")

connection = psycopg2.connect(DATABASE_URL)
cursor = connection.cursor()


# ============================================================
# CREATE TEMPORARY STAGING TABLE
# ============================================================

print("\nCreating temporary staging table...")

cursor.execute(
    """
    CREATE TEMP TABLE work_logs_staging
    (
        LIKE work_logs INCLUDING DEFAULTS
    )
    ON COMMIT PRESERVE ROWS;
    """
)

connection.commit()


# ============================================================
# IMPORT CONFIGURATION
# ============================================================

chunk_size = 50_000
total_rows = len(declarations)

total_inserted = 0
total_skipped = 0
processed_rows = 0


# ============================================================
# RESUME-SAFE BULK IMPORT
# ============================================================

print("\nStarting resume-safe work-log import...")

try:

    for start in range(0, total_rows, chunk_size):

        end = min(start + chunk_size, total_rows)

        chunk = declarations.iloc[start:end]

        buffer = io.StringIO()

        writer = csv.writer(
            buffer,
            lineterminator="\n"
        )

        for row in chunk.itertuples(
            index=False,
            name=None
        ):
            writer.writerow(row)

        buffer.seek(0)

        # Clear staging table before loading next batch.
        cursor.execute(
            "TRUNCATE TABLE work_logs_staging;"
        )

        # Load batch into temporary staging table.
        cursor.copy_expert(
            """
            COPY work_logs_staging
            (
                id,
                created_at,
                date,
                duration,
                source,
                user_id,
                task_id
            )
            FROM STDIN
            WITH (FORMAT CSV);
            """,
            buffer
        )

        # Insert only IDs that do not already exist.
        cursor.execute(
            """
            INSERT INTO work_logs
            (
                id,
                created_at,
                date,
                duration,
                source,
                user_id,
                task_id
            )
            SELECT
                id,
                created_at,
                date,
                duration,
                source,
                user_id,
                task_id
            FROM work_logs_staging
            ON CONFLICT (id) DO NOTHING;
            """
        )

        inserted = cursor.rowcount
        skipped = len(chunk) - inserted

        # Commit this batch.
        connection.commit()

        total_inserted += inserted
        total_skipped += skipped
        processed_rows += len(chunk)

        print(
            f"Processed {processed_rows:,} / {total_rows:,} | "
            f"New: {total_inserted:,} | "
            f"Skipped: {total_skipped:,}"
        )

    print("\nWork-log import completed!")

    print(f"Total processed: {processed_rows:,}")
    print(f"New records inserted: {total_inserted:,}")
    print(f"Existing records skipped: {total_skipped:,}")

except Exception as error:

    connection.rollback()

    print("\nERROR: Work-log import failed.")
    print(error)

    raise

finally:

    cursor.close()
    connection.close()


# ============================================================
# FINAL MESSAGE
# ============================================================

print("\nDatabase connection closed.")
