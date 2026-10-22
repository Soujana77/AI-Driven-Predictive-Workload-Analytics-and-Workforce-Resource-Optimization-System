from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


def main():
    print("=" * 80)
    print("VALIDATE CONTINUOUS FORECASTING DATASET")
    print("=" * 80)

    file_path = (
        PROCESSED_DATA_DIR /
        "employee_weekly_forecasting.csv"
    )

    print("\nLoading forecasting dataset...")

    forecasting = pd.read_csv(
        file_path,
        parse_dates=["week_start"]
    )

    print("Dataset loaded successfully.")

    print(f"\nRows: {len(forecasting):,}")
    print(
        f"Employees: "
        f"{forecasting['user_id'].nunique():,}"
    )
    print(
        f"Weeks: "
        f"{forecasting['week_start'].nunique():,}"
    )

    print("\n" + "=" * 80)
    print("1. MISSING VALUE CHECK")
    print("=" * 80)

    missing_values = forecasting.isna().sum()

    print(missing_values)

    print(
        f"\nTotal missing values: "
        f"{missing_values.sum():,}"
    )

    print("\n" + "=" * 80)
    print("2. DUPLICATE EMPLOYEE-WEEK CHECK")
    print("=" * 80)

    duplicate_count = (
        forecasting
        .duplicated(
            subset=[
                "user_id",
                "week_start"
            ]
        )
        .sum()
    )

    print(
        f"Duplicate employee-week rows: "
        f"{duplicate_count:,}"
    )

    print("\n" + "=" * 80)
    print("3. NEGATIVE WORKLOAD CHECK")
    print("=" * 80)

    negative_count = (
        forecasting["workload_hours"] < 0
    ).sum()

    print(
        f"Negative workload records: "
        f"{negative_count:,}"
    )

    print("\n" + "=" * 80)
    print("4. TEAM INFORMATION CHECK")
    print("=" * 80)

    missing_team_count = (
        forecasting["user_team_id"]
        .isna()
        .sum()
    )

    print(
        f"Missing team IDs: "
        f"{missing_team_count:,}"
    )

    print("\n" + "=" * 80)
    print("5. DATE CHECK")
    print("=" * 80)

    print(
        f"Minimum week: "
        f"{forecasting['week_start'].min()}"
    )

    print(
        f"Maximum week: "
        f"{forecasting['week_start'].max()}"
    )

    print(
        f"Unique weeks: "
        f"{forecasting['week_start'].nunique():,}"
    )

    print("\n" + "=" * 80)
    print("6. ACTIVITY CHECK")
    print("=" * 80)

    activity_counts = (
        forecasting[
            "has_recorded_work"
        ]
        .value_counts()
        .sort_index()
    )

    print(activity_counts)

    print(
        "\nRecorded weeks:"
    )

    print(
        f"  {(forecasting['has_recorded_work'] == 1).sum():,}"
    )

    print(
        "\nGenerated zero-work weeks:"
    )

    print(
        f"  {(forecasting['has_recorded_work'] == 0).sum():,}"
    )

    print("\n" + "=" * 80)
    print("7. WORKLOAD CHECK")
    print("=" * 80)

    print(
        forecasting[
            "workload_hours"
        ].describe()
    )

    print("\nExtreme workload records:")

    extreme_count = (
        forecasting["extreme_record_count"] > 0
    ).sum()

    print(
        f"  {extreme_count:,}"
    )

    print("\n" + "=" * 80)
    print("8. EMPLOYEE TIMELINE CHECK")
    print("=" * 80)

    employee_weeks = (
        forecasting
        .groupby("user_id")["week_start"]
        .nunique()
    )

    print(
        "Employee timeline statistics:"
    )

    print(
        employee_weeks.describe()
    )

    expected_weeks = (
        forecasting["week_start"].nunique()
    )

    incomplete_employees = (
        employee_weeks < expected_weeks
    ).sum()

    print(
        f"\nEmployees with fewer than "
        f"{expected_weeks} weeks: "
        f"{incomplete_employees:,}"
    )

    print("\n" + "=" * 80)
    print("9. FINAL VALIDATION STATUS")
    print("=" * 80)

    validation_passed = True

    if missing_values.sum() > 0:
        print("FAIL: Missing values found.")
        validation_passed = False
    else:
        print("PASS: No missing values.")

    if duplicate_count > 0:
        print(
            "FAIL: Duplicate employee-week rows found."
        )
        validation_passed = False
    else:
        print(
            "PASS: No duplicate employee-week rows."
        )

    if negative_count > 0:
        print("FAIL: Negative workload found.")
        validation_passed = False
    else:
        print("PASS: No negative workload.")

    if missing_team_count > 0:
        print("FAIL: Missing team IDs found.")
        validation_passed = False
    else:
        print("PASS: All employees have team IDs.")

    if validation_passed:
        print("\n" + "=" * 80)
        print("VALIDATION PASSED")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("VALIDATION FAILED")
        print("=" * 80)


if __name__ == "__main__":
    main()