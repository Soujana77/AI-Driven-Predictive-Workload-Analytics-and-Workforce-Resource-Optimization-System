
import os
import csv
import json
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
    raise ValueError("DATABASE_URL not found in backend/.env")


OUTPUT_DIR = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "clean_workload_dataset.csv"
)

REPORT_FILE = os.path.join(
    OUTPUT_DIR,
    "cleaning_report.json"
)

TICKS_PER_HOUR = 3_600_000_000_000
CHUNK_SIZE = 50_000


# ============================================================
# DATABASE QUERIES
# ============================================================

QUALITY_QUERY = """
SELECT
    COUNT(*) AS total_records,

    COUNT(*) FILTER (
        WHERE duration < 0
    ) AS negative_records,

    COUNT(*) FILTER (
        WHERE duration = 0
    ) AS zero_records,

    COUNT(*) FILTER (
        WHERE duration > 0
    ) AS positive_records,

    COUNT(*) FILTER (
        WHERE duration > 86400000000000
    ) AS above_24_hours

FROM work_logs;
"""


DATA_QUERY = """
SELECT
    id::text,
    date,
    user_id::text,
    task_id::text,
    source,
    duration::numeric / 3600000000000 AS duration_hours,
    duration > 86400000000000 AS is_over_24_hours

FROM work_logs

WHERE duration > 0

ORDER BY date, user_id;
"""


# ============================================================
# BUILD CLEAN DATASET
# ============================================================

def build_dataset():

    print("=" * 60)
    print("CLEAN WORKLOAD DATASET GENERATION")
    print("=" * 60)

    connection = None
    data_cursor = None

    try:

        print("\nConnecting to PostgreSQL...")

        connection = psycopg2.connect(DATABASE_URL)

        print("Connection successful!")

        # ----------------------------------------------------
        # DATA QUALITY SUMMARY
        # ----------------------------------------------------

        summary_cursor = connection.cursor()

        summary_cursor.execute(QUALITY_QUERY)

        result = summary_cursor.fetchone()

        columns = [
            description[0]
            for description in summary_cursor.description
        ]

        report = dict(zip(columns, result))

        summary_cursor.close()

        # ----------------------------------------------------
        # STREAM DATA IN BATCHES
        # ----------------------------------------------------

        data_cursor = connection.cursor(
            name="workload_dataset_cursor"
        )

        data_cursor.itersize = CHUNK_SIZE

        data_cursor.execute(DATA_QUERY)

        exported_records = 0
        flagged_records = 0

        print("\nGenerating cleaned dataset...")

        with open(
            OUTPUT_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as csv_file:

            writer = csv.writer(csv_file)

            writer.writerow([
                "id",
                "date",
                "user_id",
                "task_id",
                "source",
                "duration_hours",
                "is_over_24_hours"
            ])

            while True:

                rows = data_cursor.fetchmany(CHUNK_SIZE)

                if not rows:
                    break

                writer.writerows(rows)

                exported_records += len(rows)

                flagged_records += sum(
                    1 for row in rows if row[6]
                )

                print(
                    f"Exported {exported_records:,} records..."
                )

        data_cursor.close()
        data_cursor = None

        # ----------------------------------------------------
        # REPORT
        # ----------------------------------------------------

        report["exported_records"] = exported_records
        report["flagged_above_24_hours"] = flagged_records
        report["excluded_negative_and_zero"] = (
            report["negative_records"] +
            report["zero_records"]
        )

        report["duration_conversion"] = (
            "duration / 3600000000000"
        )

        report["cleaning_policy"] = {
            "negative_duration": "Excluded",
            "zero_duration": "Excluded",
            "above_24_hours": "Retained and flagged",
            "original_database": "Unmodified"
        }

        with open(
            REPORT_FILE,
            "w",
            encoding="utf-8"
        ) as report_file:

            json.dump(
                report,
                report_file,
                indent=4,
                default=str
            )

        # ----------------------------------------------------
        # FINAL OUTPUT
        # ----------------------------------------------------

        print("\n" + "=" * 60)
        print("DATASET GENERATION COMPLETED")
        print("=" * 60)

        print(f"Original records: {report['total_records']:,}")
        print(f"Negative records: {report['negative_records']:,}")
        print(f"Zero records: {report['zero_records']:,}")
        print(f"Exported records: {exported_records:,}")
        print(f"Flagged records: {flagged_records:,}")

        print(f"\nDataset: {OUTPUT_FILE}")
        print(f"Report: {REPORT_FILE}")

    except Exception as error:

        print("\nDATASET GENERATION FAILED")
        print(error)

        raise

    finally:

        if data_cursor:
            data_cursor.close()

        if connection:
            connection.close()

            print("\nDatabase connection closed.")


if __name__ == "__main__":
    build_dataset()
