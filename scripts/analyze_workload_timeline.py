from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


def main():
    print("=" * 80)
    print("WORKLOAD TIMELINE ANALYSIS")
    print("=" * 80)

    file_path = (
        PROCESSED_DATA_DIR /
        "historical_workload.csv"
    )

    print("\nLoading historical workload dataset...")

    workload = pd.read_csv(
        file_path,
        parse_dates=["date"]
    )

    print("Dataset loaded successfully.")

    print("\nCreating year column...")

    workload["year"] = workload["date"].dt.year

    print("\n" + "=" * 80)
    print("RECORDS BY YEAR")
    print("=" * 80)

    yearly_records = (
        workload
        .groupby("year")
        .agg(
            records=("date", "size"),
            employees=("user_id", "nunique"),
            projects=("project_id", "nunique"),
            workload_hours=("duration_hours", "sum")
        )
        .reset_index()
    )

    print(
        yearly_records.to_string(
            index=False
        )
    )

    print("\n" + "=" * 80)
    print("RECENT YEARS")
    print("=" * 80)

    recent = yearly_records[
        yearly_records["year"] >= 2025
    ]

    print(
        recent.to_string(
            index=False
        )
    )

    print("\n" + "=" * 80)
    print("EXTREME RECORDS BY YEAR")
    print("=" * 80)

    extreme_by_year = (
        workload[
            workload["is_extreme_duration"] == True
        ]
        .groupby("year")
        .size()
        .reset_index(name="extreme_records")
    )

    print(
        extreme_by_year.to_string(
            index=False
        )
    )

    print("\n" + "=" * 80)
    print("TIMELINE ANALYSIS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()