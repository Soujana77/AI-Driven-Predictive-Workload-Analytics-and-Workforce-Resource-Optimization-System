from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODEL_DIR = PROJECT_ROOT / "models"


def main():

    print("=" * 80)
    print("TRAINING RANDOM FOREST WORKLOAD FORECASTING MODEL")
    print("=" * 80)

    train_file = PROCESSED_DATA_DIR / "train_forecasting.csv"
    validation_file = PROCESSED_DATA_DIR / "validation_forecasting.csv"

    MODEL_DIR.mkdir(exist_ok=True)

    model_file = MODEL_DIR / "random_forest_workload_model.joblib"

    # ---------------------------------------------------------------
    # 1. LOAD DATA
    # ---------------------------------------------------------------

    print("\nLoading datasets...")

    train_data = pd.read_csv(train_file)
    validation_data = pd.read_csv(validation_file)

    print(f"Training rows: {len(train_data):,}")
    print(f"Validation rows: {len(validation_data):,}")

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

    X_train = train_data[feature_columns]
    y_train = train_data[target_column]

    X_validation = validation_data[feature_columns]
    y_validation = validation_data[target_column]

    # ---------------------------------------------------------------
    # 3. CREATE RANDOM FOREST MODEL
    # ---------------------------------------------------------------

    print("\nCreating Random Forest model...")

    model = RandomForestRegressor(
        n_estimators=50,
        max_depth=15,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1
    )

    # ---------------------------------------------------------------
    # 4. TRAIN MODEL
    # ---------------------------------------------------------------

    print("Training model...")

    model.fit(
        X_train,
        y_train
    )

    print("Model training completed.")

    # ---------------------------------------------------------------
    # 5. MAKE PREDICTIONS
    # ---------------------------------------------------------------

    print("\nGenerating validation predictions...")

    predictions = model.predict(
        X_validation
    )

    # ---------------------------------------------------------------
    # 6. EVALUATE MODEL
    # ---------------------------------------------------------------

    mae = mean_absolute_error(
        y_validation,
        predictions
    )

    rmse = mean_squared_error(
        y_validation,
        predictions
    ) ** 0.5

    print("\n" + "=" * 80)
    print("RANDOM FOREST RESULTS")
    print("=" * 80)

    print(f"\nMAE:  {mae:.4f} hours")
    print(f"RMSE: {rmse:.4f} hours")

    # ---------------------------------------------------------------
    # 7. FEATURE IMPORTANCE
    # ---------------------------------------------------------------

    importance = pd.DataFrame({
        "feature": feature_columns,
        "importance": model.feature_importances_
    })

    importance = importance.sort_values(
        "importance",
        ascending=False
    )

    print("\nTop feature importance:")

    print(
        importance.head(10).to_string(index=False)
    )

    # ---------------------------------------------------------------
    # 8. SAVE MODEL
    # ---------------------------------------------------------------

    print("\nSaving model...")

    joblib.dump(
        model,
        model_file
    )

    print(f"Model saved to: {model_file}")

    # ---------------------------------------------------------------
    # 9. SAMPLE PREDICTIONS
    # ---------------------------------------------------------------

    results = validation_data[
        [
            "user_id",
            "week_start",
            "next_week_workload"
        ]
    ].copy()

    results["predicted_workload"] = predictions

    print("\nSample predictions:")

    print(
        results.head(10).to_string(index=False)
    )

    print("\n" + "=" * 80)
    print("RANDOM FOREST TRAINING COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()