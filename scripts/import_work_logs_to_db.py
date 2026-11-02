
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
    f"Declarations loaded: "
    f"{len(declarations):,}"
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

print(
    f"Invalid dates found: "
    f"{invalid_dates:,}"
)

declarations = declarations.dropna(
    subset=["date"]
).copy()

print(
    f"Records remaining: "
    f"{len(declarations):,}"
)


# ============================================================
# PREPARE VALUES FOR POSTGRESQL COPY
# ============================================================

print("\nPreparing database import...")

declarations["created_at"] = (
    declarations["created_at"]
    .dt.strftime("%Y-%m-%d %H:%M:%S.%f%z")
)

declarations["date"] = (
    declarations["date"]
    .astype(str)
)

declarations["duration"] = (
    declarations["duration"]
    .astype("int64")
)


# ============================================================
# CONNECT TO POSTGRESQL
# ============================================================

print("\nConnecting to PostgreSQL...")

connection = psycopg2.connect(
    DATABASE_URL
)

cursor = connection.cursor()


# ============================================================
# IMPORT USING POSTGRESQL COPY
# ============================================================

print("\nImporting work logs using PostgreSQL COPY...")

chunk_size = 50_000

total_rows = len(declarations)

try:

    for start in range(
        0,
        total_rows,
        chunk_size
    ):

        end = min(
            start + chunk_size,
            total_rows
        )

        chunk = declarations.iloc[
            start:end
        ]

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

        cursor.copy_expert(
            """
            COPY work_logs
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
            WITH (
                FORMAT CSV
            )
            """,
            buffer
        )

        connection.commit()

        print(
            f"Imported "
            f"{end:,} / "
            f"{total_rows:,}"
        )


    print(
        "\nWork logs imported successfully!"
    )

    print(
        f"Records inserted: "
        f"{total_rows:,}"
    )


except Exception as error:

    connection.rollback()

    print(
        "\nERROR: Work log import failed."
    )

    print(error)

    raise


finally:

    cursor.close()
    connection.close()
