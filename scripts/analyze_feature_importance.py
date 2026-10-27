from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_DIR = PROJECT_ROOT / "models"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


def main():

    print("=" * 80)
    print("ANALYZING FORECASTING FEATURE IMPORTANCE")
    print("=" * 80)

    model_file = (
        MODEL_DIR / "random_forest_workload_model.joblib"
    )

    output_file = (
        PROCESSED_DATA_DIR /
        "forecasting_feature_importance.csv"
    )

    # ---------------------------------------------------------------
    # 1. LOAD MODEL
    # ---------------------------------------------------------------

    print("\nLoading Random Forest model...")

    model = joblib.load(model_file)

    print("Model loaded successfully.")

    # ---------------------------------------------------------------
    # 2. DEFINE FEATURES
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
    # 3. EXTRACT FEATURE IMPORTANCE
    # ---------------------------------------------------------------

    print("\nCalculating feature importance...")

    importance = pd.DataFrame({
        "feature": feature_columns,
        "importance": model.feature_importances_
    })

    # ---------------------------------------------------------------
    # 4. SORT FEATURES
    # ---------------------------------------------------------------

    importance = importance.sort_values(
        "importance",
        ascending=False
    ).reset_index(drop=True)

    # ---------------------------------------------------------------
    # 5. DISPLAY RESULTS
    # ---------------------------------------------------------------

    print("\n" + "=" * 80)
    print("FEATURE IMPORTANCE")
    print("=" * 80)

    for index, row in importance.iterrows():

        print(
            f"{index + 1:2}. "
            f"{row['feature']:<25} "
            f"{row['importance']:.6f}"
        )

    # ---------------------------------------------------------------
    # 6. SAVE RESULTS
    # ---------------------------------------------------------------

    importance.to_csv(
        output_file,
        index=False
    )

    print(
        f"\nFeature importance saved to: {output_file}"
    )

    print("\n" + "=" * 80)
    print("FEATURE IMPORTANCE ANALYSIS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()
    