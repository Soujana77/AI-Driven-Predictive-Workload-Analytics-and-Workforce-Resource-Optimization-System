from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


def main():
    print("=" * 80)
    print("VALIDATE HISTORICAL WORKLOAD DATASET")
    print("=" * 80)

    file_path = (
        PROCESSED_DATA_DIR /
        "historical_workload.csv"
    )

    workload = pd.read_csv(
        file_path,
        parse_dates=["date"]
    )

    print("\nDataset loaded successfully.")

    print("\nShape:")
    print(f"  Rows: {len(workload):,}")
    print(f"  Columns: {len(workload.columns)}")

    print("\nMissing values:")

    print(
        workload.isna().sum()
    )

    print("\nNegative workload records:")

    negative_count = (
        workload["duration_hours"] < 0
    ).sum()

    print(f"  {negative_count:,}")

    print("\nZero workload records:")

    zero_count = (
        workload["duration_hours"] == 0
    ).sum()

    print(f"  {zero_count:,}")

    print("\nExtreme workload records:")

    extreme_count = (
        workload["is_extreme_duration"]
        == True
    ).sum()

    print(f"  {extreme_count:,}")

    print("\nWorkload statistics:")

    print(
        workload["duration_hours"].describe()
    )

    print("\nUnique employees:")

    print(
        f"  {workload['user_id'].nunique():,}"
    )

    print("\nUnique teams:")

    print(
        f"  {workload['user_team_id'].nunique():,}"
    )

    print("\nUnique projects:")

    print(
        f"  {workload['project_id'].nunique():,}"
    )

    print("\nUnique tasks:")

    print(
        f"  {workload['task_id'].nunique():,}"
    )

    print("\nDate range:")

    print(
        f"  {workload['date'].min()} "
        f"to "
        f"{workload['date'].max()}"
    )

    print("\nSample records:")

    print(
        workload.head(10).to_string(
            index=False
        )
    )

    print("\n" + "=" * 80)
    print("VALIDATION COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()