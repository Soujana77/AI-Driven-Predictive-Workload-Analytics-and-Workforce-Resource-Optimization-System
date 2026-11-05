
import os
import json
import psycopg2

from dotenv import load_dotenv


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

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
# REPORT DIRECTORY
# ============================================================

REPORT_DIR = os.path.join(
    PROJECT_ROOT,
    "reports"
)

os.makedirs(
    REPORT_DIR,
    exist_ok=True
)

REPORT_FILE = os.path.join(
    REPORT_DIR,
    "database_quality_report.json"
)


# ============================================================
# DATABASE QUALITY ANALYSIS
# ============================================================

QUERY = """
SELECT
    COUNT(*) AS total_records,

    COUNT(*) FILTER (
        WHERE duration < 0
    ) AS negative_records,

    COUNT(*) FILTER (
        WHERE duration = 0
    ) AS zero_records,

    COUNT(*) FILTER (
        WHERE duration > 86400000000000
    ) AS above_24_hours,

    COUNT(*) FILTER (
        WHERE duration > 360000000000000
    ) AS above_100_hours,

    COUNT(*) FILTER (
        WHERE duration > 3600000000000000
    ) AS above_1000_hours,

    MIN(duration::numeric / 3600000000000)
        AS minimum_hours,

    MAX(duration::numeric / 3600000000000)
        AS maximum_hours,

    AVG(duration::numeric / 3600000000000)
        AS average_hours,

    PERCENTILE_CONT(0.25)
        WITHIN GROUP (
            ORDER BY duration::numeric / 3600000000000
        ) AS p25_hours,

    PERCENTILE_CONT(0.50)
        WITHIN GROUP (
            ORDER BY duration::numeric / 3600000000000
        ) AS median_hours,

    PERCENTILE_CONT(0.75)
        WITHIN GROUP (
            ORDER BY duration::numeric / 3600000000000
        ) AS p75_hours,

    MIN(date) AS earliest_date,

    MAX(date) AS latest_date

FROM work_logs;
"""


# ============================================================
# EXECUTE ANALYSIS
# ============================================================

print("=" * 60)
print("WORKFORCE DATABASE QUALITY ANALYSIS")
print("=" * 60)

connection = None

try:

    print("\nConnecting to PostgreSQL...")

    connection = psycopg2.connect(
        DATABASE_URL
    )

    cursor = connection.cursor()

    print("Database connection successful!")

    print("\nAnalyzing work-log records...")

    cursor.execute(QUERY)

    row = cursor.fetchone()

    columns = [
        description[0]
        for description in cursor.description
    ]

    report = dict(
        zip(columns, row)
    )

    cursor.close()

    # Convert database values into JSON-compatible values.
    for key, value in report.items():

        if hasattr(value, "isoformat"):
            report[key] = value.isoformat()

        elif value is not None:
            report[key] = float(value) if key.endswith("_hours") else int(value)


    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    print("\nWORK-LOG QUALITY RESULTS")

    for key, value in report.items():

        print(
            f"{key.replace('_', ' ').title():25}: {value}"
        )


    # ========================================================
    # SAVE REPORT
    # ========================================================

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )

    print("\n" + "=" * 60)

    print("Analysis completed successfully!")

    print(
        f"Report saved to: {REPORT_FILE}"
    )

    print("=" * 60)


except Exception as error:

    print("\nDATABASE ANALYSIS FAILED")

    print(error)

    raise

finally:

    if connection:
        connection.close()

        print("\nDatabase connection closed.")
