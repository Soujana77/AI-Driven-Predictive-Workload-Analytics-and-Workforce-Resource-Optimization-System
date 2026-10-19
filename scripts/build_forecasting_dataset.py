from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


def main():
    print("=" * 80)
    print("BUILD EMPLOYEE WEEKLY FORECASTING DATASET")
    print("=" * 80)

    input_file = (
        PROCESSED_DATA_DIR /
        "historical_workload.csv"
    )

    output_file = (
        PROCESSED_DATA_DIR /
        "employee_weekly_workload.csv"
    )

    print("\nLoading historical workload dataset...")

    workload = pd.read_csv(
        input_file,
        parse_dates=["date"]
    )

    print("Dataset loaded successfully.")

    print(f"Rows loaded: {len(workload):,}")

    print("\nFiltering historical modeling period...")

    workload = workload[
        (workload["date"].dt.year >= 2019)
        & (workload["date"].dt.year <= 2024)
    ].copy()

    print(
        f"Historical records retained: "
        f"{len(workload):,}"
    )

    print("\nCreating week start date...")

    workload["week_start"] = (
        workload["date"]
        - pd.to_timedelta(
            workload["date"].dt.weekday,
            unit="D"
        )
    )

    workload["week_start"] = (
        workload["week_start"]
        .dt.normalize()
    )

    print("\nAggregating employee workload by week...")

    weekly_workload = (
        workload
        .groupby(
            [
                "user_id",
                "user_team_id",
                "week_start"
            ],
            as_index=False
        )
        .agg(
            workload_hours=(
                "duration_hours",
                "sum"
            ),
            active_task_count=(
                "task_id",
                "nunique"
            ),
            active_project_count=(
                "project_id",
                "nunique"
            ),
            work_log_count=(
                "task_id",
                "size"
            ),
            extreme_record_count=(
                "is_extreme_duration",
                "sum"
            )
        )
    )

    print("\nWeekly dataset created.")

    print(
        f"Rows: {len(weekly_workload):,}"
    )

    print(
        f"Employees: "
        f"{weekly_workload['user_id'].nunique():,}"
    )

    print(
        f"Weeks: "
        f"{weekly_workload['week_start'].nunique():,}"
    )

    print("\nSorting dataset...")

    weekly_workload = weekly_workload.sort_values(
        [
            "user_id",
            "week_start"
        ]
    )

    print("\nSaving forecasting dataset...")

    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    weekly_workload.to_csv(
        output_file,
        index=False
    )

    print("\n" + "=" * 80)
    print("FORECASTING DATASET CREATED")
    print("=" * 80)

    print(
        f"\nSaved to:\n  {output_file}"
    )

    print("\nColumns:")

    for column in weekly_workload.columns:
        print(f"  - {column}")

    print("\nDate range:")

    print(
        f"  {weekly_workload['week_start'].min()}"
        f" to "
        f"{weekly_workload['week_start'].max()}"
    )

    print("\nWorkload statistics:")

    print(
        weekly_workload[
            "workload_hours"
        ].describe()
    )

    print("\nSample records:")

    print(
        weekly_workload.head(10).to_string(
            index=False
        )
    )

    print("\n" + "=" * 80)
    print("FORECASTING DATASET BUILD COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()