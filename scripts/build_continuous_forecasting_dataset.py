from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


def main():
    print("=" * 80)
    print("BUILD CONTINUOUS EMPLOYEE-WEEK DATASET")
    print("=" * 80)

    input_file = (
        PROCESSED_DATA_DIR /
        "employee_weekly_workload.csv"
    )

    output_file = (
        PROCESSED_DATA_DIR /
        "employee_weekly_forecasting.csv"
    )

    print("\nLoading employee weekly workload...")

    workload = pd.read_csv(
        input_file,
        parse_dates=["week_start"]
    )

    print("Dataset loaded successfully.")

    print(
        f"Existing rows: {len(workload):,}"
    )

    print("\nFinding employee activity periods...")

    activity_periods = (
        workload
        .groupby("user_id")
        .agg(
            first_active_week=(
                "week_start",
                "min"
            ),
            last_active_week=(
                "week_start",
                "max"
            )
        )
        .reset_index()
    )

    print(
        f"Employees found: "
        f"{len(activity_periods):,}"
    )

    print("\nCreating complete weekly timelines...")

    employee_ranges = []

    for _, employee in activity_periods.iterrows():

        weeks = pd.date_range(
            start=employee["first_active_week"],
            end=employee["last_active_week"],
            freq="7D"
        )

        employee_ranges.append(
            pd.DataFrame(
                {
                    "user_id": employee["user_id"],
                    "week_start": weeks
                }
            )
        )

    complete_timeline = pd.concat(
        employee_ranges,
        ignore_index=True
    )

    print(
        f"Complete timeline rows: "
        f"{len(complete_timeline):,}"
    )

    print("\nMerging recorded workload...")

    forecasting = complete_timeline.merge(
        workload,
        on=[
            "user_id",
            "week_start"
        ],
        how="left"
    )

    print("\nFilling missing workload observations...")

    numeric_columns = [
        "workload_hours",
        "active_task_count",
        "active_project_count",
        "work_log_count",
        "extreme_record_count"
    ]

    for column in numeric_columns:
        forecasting[column] = (
            forecasting[column]
            .fillna(0)
        )

    print("\nRestoring employee team information...")

    team_mapping = (
        workload[
            [
                "user_id",
                "user_team_id"
            ]
        ]
        .drop_duplicates(
            subset=["user_id"]
        )
    )

    forecasting = forecasting.merge(
        team_mapping,
        on="user_id",
        how="left"
    )

    print("\nCreating activity indicator...")

    forecasting["has_recorded_work"] = (
        forecasting["work_log_count"] > 0
    ).astype(int)

    print("\nSorting dataset...")

    forecasting = forecasting.sort_values(
        [
            "user_id",
            "week_start"
        ]
    )

    forecasting = forecasting[
        [
            "user_id",
            "user_team_id",
            "week_start",
            "workload_hours",
            "active_task_count",
            "active_project_count",
            "work_log_count",
            "extreme_record_count",
            "has_recorded_work"
        ]
    ]

    print("\nSaving forecasting dataset...")

    forecasting.to_csv(
        output_file,
        index=False
    )

    print("\n" + "=" * 80)
    print("CONTINUOUS FORECASTING DATASET CREATED")
    print("=" * 80)

    print(
        f"\nSaved to:\n  {output_file}"
    )

    print(
        f"\nRows: "
        f"{len(forecasting):,}"
    )

    print(
        f"Employees: "
        f"{forecasting['user_id'].nunique():,}"
    )

    print(
        f"Weeks: "
        f"{forecasting['week_start'].nunique():,}"
    )

    print("\nMissing values:")

    print(
        forecasting.isna().sum()
    )

    print("\nRecorded vs missing workload weeks:")

    print(
        forecasting[
            "has_recorded_work"
        ].value_counts()
        .sort_index()
    )

    print("\nWorkload statistics:")

    print(
        forecasting[
            "workload_hours"
        ].describe()
    )

    print("\nSample records:")

    print(
        forecasting.head(10).to_string(
            index=False
        )
    )

    print("\n" + "=" * 80)
    print("CONTINUOUS DATASET BUILD COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()