from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


def main():
    print("=" * 80)
    print("VALIDATE FORECASTING FEATURES")
    print("=" * 80)

    file_path = (
        PROCESSED_DATA_DIR /
        "employee_forecasting_features.csv"
    )

    print("\nLoading feature dataset...")

    features = pd.read_csv(
        file_path,
        parse_dates=["week_start"]
    )

    print("Dataset loaded successfully.")

    print(
        f"\nRows: {len(features):,}"
    )

    print(
        f"Columns: {len(features.columns)}"
    )

    print(
        f"Employees: "
        f"{features['user_id'].nunique():,}"
    )

    # ------------------------------------------------------------------
    # 1. MISSING VALUE CHECK
    # ------------------------------------------------------------------

    print("\n" + "=" * 80)
    print("1. MISSING VALUE CHECK")
    print("=" * 80)

    missing_values = features.isna().sum()

    print(missing_values)

    total_missing = missing_values.sum()

    print(
        f"\nTotal missing values: "
        f"{total_missing:,}"
    )

    # ------------------------------------------------------------------
    # 2. DUPLICATE CHECK
    # ------------------------------------------------------------------

    print("\n" + "=" * 80)
    print("2. DUPLICATE EMPLOYEE-WEEK CHECK")
    print("=" * 80)

    duplicate_count = (
        features
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

    # ------------------------------------------------------------------
    # 3. NEGATIVE VALUE CHECK
    # ------------------------------------------------------------------

    print("\n" + "=" * 80)
    print("3. NEGATIVE VALUE CHECK")
    print("=" * 80)

    numeric_columns = [
        "workload_hours",
        "active_task_count",
        "active_project_count",
        "work_log_count",
        "extreme_record_count",
        "lag_1_week",
        "lag_2_week",
        "lag_4_week",
        "lag_8_week",
        "rolling_mean_4",
        "rolling_mean_8",
        "rolling_std_4",
        "task_count_lag_1",
        "project_count_lag_1",
        "work_log_count_lag_1",
        "next_week_workload"
    ]

    negative_counts = {}

    for column in numeric_columns:
        count = (
            features[column] < 0
        ).sum()

        negative_counts[column] = count

        print(
            f"{column}: {count:,}"
        )

    # ------------------------------------------------------------------
    # 4. TARGET CHECK
    # ------------------------------------------------------------------

    print("\n" + "=" * 80)
    print("4. TARGET CHECK")
    print("=" * 80)

    print(
        features[
            "next_week_workload"
        ].describe()
    )

    zero_target_count = (
        features[
            "next_week_workload"
        ] == 0
    ).sum()

    print(
        f"\nZero-workload target rows: "
        f"{zero_target_count:,}"
    )

    # ------------------------------------------------------------------
    # 5. LAG CONSISTENCY CHECK
    # ------------------------------------------------------------------

    print("\n" + "=" * 80)
    print("5. LAG CONSISTENCY CHECK")
    print("=" * 80)

    test_employee = (
        features["user_id"]
        .value_counts()
        .index[0]
    )

    employee_data = (
        features[
            features["user_id"] == test_employee
        ]
        .sort_values("week_start")
        .copy()
    )

    if len(employee_data) >= 2:

        first_row = employee_data.iloc[1]

        expected_lag_1 = (
            employee_data.iloc[0]["workload_hours"]
        )

        actual_lag_1 = (
            first_row["lag_1_week"]
        )

        print(
            f"Test employee: {test_employee}"
        )

        print(
            f"Expected lag_1_week: "
            f"{expected_lag_1}"
        )

        print(
            f"Actual lag_1_week: "
            f"{actual_lag_1}"
        )

        if expected_lag_1 == actual_lag_1:
            print("PASS: lag_1_week is correct.")
        else:
            print("FAIL: lag_1_week mismatch.")

    # ------------------------------------------------------------------
    # 6. TARGET CONSISTENCY CHECK
    # ------------------------------------------------------------------

    print("\n" + "=" * 80)
    print("6. TARGET CONSISTENCY CHECK")
    print("=" * 80)

    if len(employee_data) >= 2:

        first_row = employee_data.iloc[0]

        second_row = employee_data.iloc[1]

        expected_target = (
            second_row["workload_hours"]
        )

        actual_target = (
            first_row["next_week_workload"]
        )

        print(
            f"Expected next week workload: "
            f"{expected_target}"
        )

        print(
            f"Actual target: "
            f"{actual_target}"
        )

        if expected_target == actual_target:
            print(
                "PASS: next_week_workload is correct."
            )
        else:
            print(
                "FAIL: next_week_workload mismatch."
            )

    # ------------------------------------------------------------------
    # 7. DATE ORDER CHECK
    # ------------------------------------------------------------------

    print("\n" + "=" * 80)
    print("7. DATE ORDER CHECK")
    print("=" * 80)

    date_order_errors = 0

    for _, employee_data in features.groupby("user_id"):

        dates = employee_data["week_start"]

        if not dates.is_monotonic_increasing:
            date_order_errors += 1

    print(
        f"Employees with date ordering errors: "
        f"{date_order_errors:,}"
    )

    # ------------------------------------------------------------------
    # 8. FEATURE STATISTICS
    # ------------------------------------------------------------------

    print("\n" + "=" * 80)
    print("8. FEATURE STATISTICS")
    print("=" * 80)

    statistics = features[
        numeric_columns
    ].describe().T

    print(statistics)

    # ------------------------------------------------------------------
    # 9. FINAL VALIDATION
    # ------------------------------------------------------------------

    print("\n" + "=" * 80)
    print("9. FINAL VALIDATION STATUS")
    print("=" * 80)

    validation_passed = True

    if total_missing > 0:
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

    if sum(negative_counts.values()) > 0:
        print(
            "FAIL: Negative values found."
        )
        validation_passed = False
    else:
        print(
            "PASS: No negative numeric values."
        )

    if date_order_errors > 0:
        print(
            "FAIL: Date ordering errors found."
        )
        validation_passed = False
    else:
        print(
            "PASS: Employee timelines are ordered."
        )

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