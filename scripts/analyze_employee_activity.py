from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


def main():
    print("=" * 80)
    print("EMPLOYEE ACTIVITY ANALYSIS")
    print("=" * 80)

    file_path = (
        PROCESSED_DATA_DIR /
        "employee_weekly_workload.csv"
    )

    print("\nLoading employee weekly workload...")

    workload = pd.read_csv(
        file_path,
        parse_dates=["week_start"]
    )

    print("Dataset loaded successfully.")

    print(f"Rows: {len(workload):,}")

    print("\nCalculating employee activity periods...")

    employee_activity = (
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
            ),
            active_weeks=(
                "week_start",
                "nunique"
            ),
            total_workload_hours=(
                "workload_hours",
                "sum"
            )
        )
        .reset_index()
    )

    employee_activity["calendar_weeks"] = (
        (
            employee_activity["last_active_week"]
            - employee_activity["first_active_week"]
        ).dt.days
        / 7
    ).round().astype(int) + 1

    employee_activity["missing_weeks"] = (
        employee_activity["calendar_weeks"]
        - employee_activity["active_weeks"]
    )

    employee_activity["activity_ratio"] = (
        employee_activity["active_weeks"]
        / employee_activity["calendar_weeks"]
    )

    print("\n" + "=" * 80)
    print("EMPLOYEE ACTIVITY SUMMARY")
    print("=" * 80)

    print(
        employee_activity[
            [
                "active_weeks",
                "calendar_weeks",
                "missing_weeks",
                "activity_ratio"
            ]
        ].describe()
    )

    print("\n" + "=" * 80)
    print("EMPLOYEES WITH MOST ACTIVITY GAPS")
    print("=" * 80)

    largest_gaps = (
        employee_activity
        .sort_values(
            "missing_weeks",
            ascending=False
        )
        .head(20)
    )

    print(
        largest_gaps.to_string(
            index=False
        )
    )

    print("\n" + "=" * 80)
    print("EMPLOYEES WITH CONTINUOUS ACTIVITY")
    print("=" * 80)

    continuous = employee_activity[
        employee_activity["missing_weeks"] == 0
    ]

    print(
        f"\nEmployees with no gaps: "
        f"{len(continuous):,}"
    )

    print("\n" + "=" * 80)
    print("EMPLOYEES WITH LARGE GAPS")
    print("=" * 80)

    large_gaps = employee_activity[
        employee_activity["missing_weeks"] >= 20
    ]

    print(
        f"\nEmployees with 20+ missing weeks: "
        f"{len(large_gaps):,}"
    )

    print("\n" + "=" * 80)
    print("ACTIVITY ANALYSIS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()
    