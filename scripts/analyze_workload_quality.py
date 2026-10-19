from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def main():
    print("=" * 80)
    print("WORKLOAD DATA QUALITY ANALYSIS")
    print("=" * 80)

    file_path = RAW_DATA_DIR / "declarations.csv"

    declarations = pd.read_csv(
        file_path,
        usecols=[
            "date",
            "duration",
            "user_id",
            "task_id"
        ]
    )

    declarations["date"] = pd.to_datetime(
        declarations["date"],
        errors="coerce"
    )

    # Convert nanoseconds to hours for analysis.
    declarations["duration_hours"] = (
        declarations["duration"] / 1_000_000_000 / 3600
    )

    print("\nTotal records:")
    print(f"  {len(declarations):,}")

    print("\nDuration in hours:")
    print(declarations["duration_hours"].describe())

    print("\nNegative duration records:")
    negative_count = (
        declarations["duration_hours"] < 0
    ).sum()

    print(f"  {negative_count:,}")

    print("\nZero duration records:")
    zero_count = (
        declarations["duration_hours"] == 0
    ).sum()

    print(f"  {zero_count:,}")

    print("\nDuration greater than 24 hours:")
    over_24_count = (
        declarations["duration_hours"] > 24
    ).sum()

    print(f"  {over_24_count:,}")

    print("\nDuration greater than 100 hours:")
    over_100_count = (
        declarations["duration_hours"] > 100
    ).sum()

    print(f"  {over_100_count:,}")

    print("\nDuration greater than 1000 hours:")
    over_1000_count = (
        declarations["duration_hours"] > 1000
    ).sum()

    print(f"  {over_1000_count:,}")

    print("\nRecords with duration greater than 1000 hours:")

    extreme_records = declarations[
        declarations["duration_hours"] > 1000
    ]

    print(
        extreme_records[
            [
                "date",
                "duration",
                "duration_hours",
                "user_id",
                "task_id"
            ]
        ].to_string(index=False)
    )

    print("\nRecords with negative duration:")

    negative_records = declarations[
        declarations["duration_hours"] < 0
    ]

    print(
        negative_records[
            [
                "date",
                "duration",
                "duration_hours",
                "user_id",
                "task_id"
            ]
        ].to_string(index=False)
    )

    print(f"  {over_1000_count:,}")

    print("\nSmallest durations in hours:")
    print(
        declarations["duration_hours"]
        .nsmallest(10)
        .to_string(index=False)
    )

    print("\nLargest durations in hours:")
    print(
        declarations["duration_hours"]
        .nlargest(10)
        .to_string(index=False)
    )

    print("\nMissing values:")

    print(
        declarations[
            ["date", "duration", "user_id", "task_id"]
        ]
        .isna()
        .sum()
    )

    print("\nSuspicious future dates:")

    future_dates = declarations[
        declarations["date"] >= "2029-01-01"
    ]

    print(f"  Records from 2029 onward: {len(future_dates):,}")

    print("\nDate range:")
    print(f"  Minimum: {declarations['date'].min()}")
    print(f"  Maximum: {declarations['date'].max()}")

    print("\n" + "=" * 80)
    print("QUALITY ANALYSIS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()