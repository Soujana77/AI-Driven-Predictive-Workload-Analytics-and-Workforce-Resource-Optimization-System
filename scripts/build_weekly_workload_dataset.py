
import os
import csv
import psycopg2

from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

load_dotenv(
    os.path.join(PROJECT_ROOT, "backend", ".env")
)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found.")

OUTPUT_DIR = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "weekly_employee_workload.csv"
)

TICKS_PER_HOUR = 3_600_000_000_000


# ============================================================
# WEEKLY AGGREGATION QUERY
# ============================================================

QUERY = """
SELECT
    user_id::text AS employee_id,

    DATE_TRUNC('week', date)::date AS week_start,

    ROUND(
        SUM(duration::numeric) / %s,
        4
    ) AS total_workload_hours,

    COUNT(*) AS work_log_count,

    COUNT(DISTINCT task_id) AS unique_tasks,

    COUNT(*) FILTER (
        WHERE duration > 86400000000000
    ) AS flagged_work_logs

FROM work_logs

WHERE duration > 0

GROUP BY
    user_id,
    DATE_TRUNC('week', date)

ORDER BY
    user_id,
    week_start;
"""


# ============================================================
# BUILD WEEKLY DATASET
# ============================================================

def build_weekly_dataset():

    connection = None

    print("=" * 55)
    print("WEEKLY EMPLOYEE WORKLOAD AGGREGATION")
    print("=" * 55)

    try:

        print("\nConnecting to PostgreSQL...")

        connection = psycopg2.connect(DATABASE_URL)

        cursor = connection.cursor(
            name="weekly_workload_cursor"
        )

        cursor.itersize = 10000

        cursor.execute(
            QUERY,
            (TICKS_PER_HOUR,)
        )

        exported = 0

        print("\nAggregating employee workloads...")

        with open(
            OUTPUT_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "employee_id",
                "week_start",
                "total_workload_hours",
                "work_log_count",
                "unique_tasks",
                "flagged_work_logs"
            ])

            while True:

                rows = cursor.fetchmany(10000)

                if not rows:
                    break

                writer.writerows(rows)

                exported += len(rows)

                print(
                    f"Exported weekly records: {exported:,}"
                )

        cursor.close()

        print("\n" + "=" * 55)
        print("WEEKLY DATASET CREATED SUCCESSFULLY")
        print("=" * 55)

        print(f"Weekly records: {exported:,}")
        print(f"Output: {OUTPUT_FILE}")

    except Exception as error:

        print("\nAGGREGATION FAILED")
        print(error)

        raise

    finally:

        if connection:
            connection.close()

            print("\nDatabase connection closed.")


if __name__ == "__main__":
    build_weekly_dataset()
