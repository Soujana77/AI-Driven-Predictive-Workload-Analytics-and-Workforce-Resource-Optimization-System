from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


def main():
    print("=" * 80)
    print("BUILD FORECASTING FEATURES")
    print("=" * 80)

    input_file = (
        PROCESSED_DATA_DIR /
        "employee_weekly_forecasting.csv"
    )

    output_file = (
        PROCESSED_DATA_DIR /
        "employee_forecasting_features.csv"
    )

    # ------------------------------------------------------------------
    # 1. LOAD DATASET
    # ------------------------------------------------------------------

    print("\nLoading continuous forecasting dataset...")

    forecasting = pd.read_csv(
        input_file,
        parse_dates=["week_start"]
    )

    print("Dataset loaded successfully.")

    print(
        f"Rows loaded: {len(forecasting):,}"
    )

    # ------------------------------------------------------------------
    # 2. SORT DATA
    # ------------------------------------------------------------------

    print("\nSorting data by employee and week...")

    forecasting = forecasting.sort_values(
        [
            "user_id",
            "week_start"
        ]
    ).copy()

    # ------------------------------------------------------------------
    # 3. CREATE LAG FEATURES
    # ------------------------------------------------------------------

    print("\nCreating workload lag features...")

    forecasting["lag_1_week"] = (
        forecasting
        .groupby("user_id")["workload_hours"]
        .shift(1)
    )

    forecasting["lag_2_week"] = (
        forecasting
        .groupby("user_id")["workload_hours"]
        .shift(2)
    )

    forecasting["lag_4_week"] = (
        forecasting
        .groupby("user_id")["workload_hours"]
        .shift(4)
    )

    forecasting["lag_8_week"] = (
        forecasting
        .groupby("user_id")["workload_hours"]
        .shift(8)
    )

    # ------------------------------------------------------------------
    # 4. CREATE ROLLING FEATURES
    # ------------------------------------------------------------------

    print("\nCreating rolling workload features...")

    forecasting["rolling_mean_4"] = (
        forecasting
        .groupby("user_id")["workload_hours"]
        .transform(
            lambda x:
            x.shift(1).rolling(
                window=4,
                min_periods=1
            ).mean()
        )
    )

    forecasting["rolling_mean_8"] = (
        forecasting
        .groupby("user_id")["workload_hours"]
        .transform(
            lambda x:
            x.shift(1).rolling(
                window=8,
                min_periods=1
            ).mean()
        )
    )

    forecasting["rolling_std_4"] = (
        forecasting
        .groupby("user_id")["workload_hours"]
        .transform(
            lambda x:
            x.shift(1).rolling(
                window=4,
                min_periods=2
            ).std()
        )
    )

    # ------------------------------------------------------------------
    # 5. CREATE TASK ACTIVITY FEATURES
    # ------------------------------------------------------------------

    print("\nCreating task activity features...")

    forecasting["task_count_lag_1"] = (
        forecasting
        .groupby("user_id")["active_task_count"]
        .shift(1)
    )

    forecasting["project_count_lag_1"] = (
        forecasting
        .groupby("user_id")["active_project_count"]
        .shift(1)
    )

    forecasting["work_log_count_lag_1"] = (
        forecasting
        .groupby("user_id")["work_log_count"]
        .shift(1)
    )

    # ------------------------------------------------------------------
    # 6. CREATE WORKLOAD TREND
    # ------------------------------------------------------------------

    print("\nCreating workload trend feature...")

    forecasting["workload_trend"] = (
        forecasting["lag_1_week"]
        - forecasting["lag_4_week"]
    )

    # ------------------------------------------------------------------
    # 7. CREATE TARGET
    # ------------------------------------------------------------------

    print("\nCreating forecasting target...")

    forecasting["next_week_workload"] = (
        forecasting
        .groupby("user_id")["workload_hours"]
        .shift(-1)
    )

    # ------------------------------------------------------------------
    # 8. REMOVE ROWS WITHOUT REQUIRED FEATURES
    # ------------------------------------------------------------------

    print("\nRemoving rows with unavailable historical features...")

    required_columns = [
        "lag_8_week",
        "rolling_mean_8",
        "next_week_workload"
    ]

    before_count = len(forecasting)

    forecasting = forecasting.dropna(
        subset=required_columns
    ).copy()

    after_count = len(forecasting)

    print(
        f"Rows removed: "
        f"{before_count - after_count:,}"
    )

    print(
        f"Rows remaining: "
        f"{after_count:,}"
    )

    # ------------------------------------------------------------------
    # 9. SELECT FINAL FEATURES
    # ------------------------------------------------------------------

    feature_columns = [
        "user_id",
        "user_team_id",
        "week_start",
        "workload_hours",
        "active_task_count",
        "active_project_count",
        "work_log_count",
        "extreme_record_count",
        "has_recorded_work",
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
        "workload_trend",
        "next_week_workload"
    ]

    forecasting = forecasting[
        feature_columns
    ]

    # ------------------------------------------------------------------
    # 10. SORT FINAL DATASET
    # ------------------------------------------------------------------

    print("\nSorting final dataset...")

    forecasting = forecasting.sort_values(
        [
            "user_id",
            "week_start"
        ]
    )

    # ------------------------------------------------------------------
    # 11. SAVE DATASET
    # ------------------------------------------------------------------

    print("\nSaving feature dataset...")

    forecasting.to_csv(
        output_file,
        index=False
    )

    # ------------------------------------------------------------------
    # 12. FINAL SUMMARY
    # ------------------------------------------------------------------

    print("\n" + "=" * 80)
    print("FORECASTING FEATURE DATASET CREATED")
    print("=" * 80)

    print(
        f"\nSaved to:\n  {output_file}"
    )

    print(
        f"\nRows: "
        f"{len(forecasting):,}"
    )

    print(
        f"Columns: "
        f"{len(forecasting.columns)}"
    )

    print(
        f"Employees: "
        f"{forecasting['user_id'].nunique():,}"
    )

    print(
        f"Weeks: "
        f"{forecasting['week_start'].nunique():,}"
    )

    print("\nFeature columns:")

    for column in forecasting.columns:
        print(f"  - {column}")

    print("\nMissing values:")

    print(
        forecasting.isna().sum()
    )

    print("\nTarget statistics:")

    print(
        forecasting[
            "next_week_workload"
        ].describe()
    )

    print("\nSample records:")

    print(
        forecasting.head(10).to_string(
            index=False
        )
    )

    print("\n" + "=" * 80)
    print("FEATURE ENGINEERING COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()