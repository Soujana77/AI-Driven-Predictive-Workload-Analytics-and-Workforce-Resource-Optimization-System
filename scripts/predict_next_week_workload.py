from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODEL_DIR = PROJECT_ROOT / "models"


def main():

    print("=" * 80)
    print("NEXT-WEEK WORKLOAD FORECAST")
    print("=" * 80)

    # ---------------------------------------------------------------
    # 1. LOAD MODEL
    # ---------------------------------------------------------------

    model_file = (
        MODEL_DIR / "random_forest_workload_model.joblib"
    )

    print("\nLoading trained model...")

    model = joblib.load(model_file)

    print("Model loaded successfully.")

    # ---------------------------------------------------------------
    # 2. LOAD LATEST DATA
    # ---------------------------------------------------------------

    input_file = (
        PROCESSED_DATA_DIR /
        "employee_forecasting_features.csv"
    )

    print("\nLoading forecasting features...")

    data = pd.read_csv(
        input_file,
        parse_dates=["week_start"]
    )

    # ---------------------------------------------------------------
    # 3. SELECT FEATURES
    # ---------------------------------------------------------------

    feature_columns = [
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
        "workload_trend"
    ]

    # ---------------------------------------------------------------
    # 4. FIND LATEST AVAILABLE WEEK
    # ---------------------------------------------------------------

    latest_week = data["week_start"].max()

    print(
        f"\nLatest forecasting week: {latest_week}"
    )

    latest_data = data[
        data["week_start"] == latest_week
    ].copy()

    print(
        f"Employees to forecast: {len(latest_data):,}"
    )

    # ---------------------------------------------------------------
    # 5. GENERATE FORECAST
    # ---------------------------------------------------------------

    print("\nGenerating next-week workload predictions...")

    predictions = model.predict(
        latest_data[feature_columns]
    )

    # ---------------------------------------------------------------
    # 6. CREATE RESULTS
    # ---------------------------------------------------------------

    forecast = latest_data[
        [
            "user_id",
            "user_team_id",
            "week_start",
            "workload_hours"
        ]
    ].copy()

    forecast["predicted_next_week_workload"] = predictions

    # Avoid negative predictions
    forecast["predicted_next_week_workload"] = (
        forecast["predicted_next_week_workload"]
        .clip(lower=0)
    )

    # ---------------------------------------------------------------
    # 7. SAVE FORECAST
    # ---------------------------------------------------------------

    output_file = (
        PROCESSED_DATA_DIR /
        "next_week_workload_forecast.csv"
    )

    forecast.to_csv(
        output_file,
        index=False
    )

    # ---------------------------------------------------------------
    # 8. DISPLAY SAMPLE
    # ---------------------------------------------------------------

    print("\n" + "=" * 80)
    print("FORECAST SAMPLE")
    print("=" * 80)

    print(
        forecast.head(10).to_string(index=False)
    )

    print("\nForecast statistics:")

    print(
        forecast[
            "predicted_next_week_workload"
        ].describe()
    )

    print(
        f"\nForecast saved to: {output_file}"
    )

    print("\n" + "=" * 80)
    print("NEXT-WEEK FORECAST COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()
    