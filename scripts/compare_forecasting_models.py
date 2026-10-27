from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODEL_DIR = PROJECT_ROOT / "models"


def calculate_metrics(actual, predicted):
    mae = mean_absolute_error(actual, predicted)
    rmse = mean_squared_error(actual, predicted) ** 0.5

    return mae, rmse


def main():

    print("=" * 80)
    print("COMPARING WORKLOAD FORECASTING MODELS")
    print("=" * 80)

    test_file = PROCESSED_DATA_DIR / "test_forecasting.csv"

    linear_model_file = (
        MODEL_DIR / "baseline_linear_regression.joblib"
    )

    random_forest_model_file = (
        MODEL_DIR / "random_forest_workload_model.joblib"
    )

    # ---------------------------------------------------------------
    # 1. LOAD TEST DATA
    # ---------------------------------------------------------------

    print("\nLoading test dataset...")

    test_data = pd.read_csv(test_file)

    print(f"Test rows: {len(test_data):,}")

    # ---------------------------------------------------------------
    # 2. SELECT FEATURES
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

    target_column = "next_week_workload"

    X_test = test_data[feature_columns]
    y_test = test_data[target_column]

    # ---------------------------------------------------------------
    # 3. LOAD MODELS
    # ---------------------------------------------------------------

    print("\nLoading trained models...")

    linear_model = joblib.load(
        linear_model_file
    )

    random_forest_model = joblib.load(
        random_forest_model_file
    )

    print("Models loaded successfully.")

    # ---------------------------------------------------------------
    # 4. GENERATE PREDICTIONS
    # ---------------------------------------------------------------

    print("\nGenerating predictions...")

    linear_predictions = linear_model.predict(
        X_test
    )

    random_forest_predictions = random_forest_model.predict(
        X_test
    )

    # ---------------------------------------------------------------
    # 5. CALCULATE METRICS
    # ---------------------------------------------------------------

    linear_mae, linear_rmse = calculate_metrics(
        y_test,
        linear_predictions
    )

    rf_mae, rf_rmse = calculate_metrics(
        y_test,
        random_forest_predictions
    )

    # ---------------------------------------------------------------
    # 6. DISPLAY RESULTS
    # ---------------------------------------------------------------

    print("\n" + "=" * 80)
    print("MODEL COMPARISON")
    print("=" * 80)

    comparison = pd.DataFrame({
        "Model": [
            "Linear Regression",
            "Random Forest"
        ],
        "MAE": [
            linear_mae,
            rf_mae
        ],
        "RMSE": [
            linear_rmse,
            rf_rmse
        ]
    })

    print(
        comparison.to_string(
            index=False,
            float_format=lambda value: f"{value:.4f}"
        )
    )

    # ---------------------------------------------------------------
    # 7. DETERMINE BEST MODEL
    # ---------------------------------------------------------------

    if rf_mae < linear_mae:
        best_model = "Random Forest"
        best_mae = rf_mae
    else:
        best_model = "Linear Regression"
        best_mae = linear_mae

    print("\n" + "=" * 80)
    print("BEST MODEL")
    print("=" * 80)

    print(f"\nBest model based on MAE: {best_model}")
    print(f"MAE: {best_mae:.4f} hours")

    # ---------------------------------------------------------------
    # 8. SAVE COMPARISON
    # ---------------------------------------------------------------

    output_file = (
        PROCESSED_DATA_DIR /
        "forecasting_model_comparison.csv"
    )

    comparison.to_csv(
        output_file,
        index=False
    )

    print(
        f"\nComparison saved to: {output_file}"
    )

    print("\n" + "=" * 80)
    print("MODEL COMPARISON COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()