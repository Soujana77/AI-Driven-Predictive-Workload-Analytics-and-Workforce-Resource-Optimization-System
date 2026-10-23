from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


def main():
    print("=" * 80)
    print("SPLIT FORECASTING DATASET")
    print("=" * 80)

    input_file = (
        PROCESSED_DATA_DIR /
        "employee_forecasting_features.csv"
    )

    train_file = (
        PROCESSED_DATA_DIR /
        "train_forecasting.csv"
    )

    validation_file = (
        PROCESSED_DATA_DIR /
        "validation_forecasting.csv"
    )

    test_file = (
        PROCESSED_DATA_DIR /
        "test_forecasting.csv"
    )

    # ------------------------------------------------------------------
    # 1. LOAD DATASET
    # ------------------------------------------------------------------

    print("\nLoading forecasting feature dataset...")

    data = pd.read_csv(
        input_file,
        parse_dates=["week_start"]
    )

    print("Dataset loaded successfully.")

    print(
        f"Total rows: {len(data):,}"
    )

    # ------------------------------------------------------------------
    # 2. SORT CHRONOLOGICALLY
    # ------------------------------------------------------------------

    print("\nSorting data chronologically...")

    data = data.sort_values(
        "week_start"
    ).reset_index(drop=True)

    print(
        f"Date range: "
        f"{data['week_start'].min()} "
        f"to "
        f"{data['week_start'].max()}"
    )

    # ------------------------------------------------------------------
    # 3. CREATE CHRONOLOGICAL SPLITS
    # ------------------------------------------------------------------

    print("\nCreating chronological splits...")

    train_data = data[
        data["week_start"].dt.year <= 2022
    ].copy()

    validation_data = data[
        data["week_start"].dt.year == 2023
    ].copy()

    test_data = data[
        data["week_start"].dt.year == 2024
    ].copy()

    # ------------------------------------------------------------------
    # 4. SAVE SPLITS
    # ------------------------------------------------------------------

    print("\nSaving datasets...")

    train_data.to_csv(
        train_file,
        index=False
    )

    validation_data.to_csv(
        validation_file,
        index=False
    )

    test_data.to_csv(
        test_file,
        index=False
    )

    # ------------------------------------------------------------------
    # 5. DISPLAY SPLIT INFORMATION
    # ------------------------------------------------------------------

    print("\n" + "=" * 80)
    print("CHRONOLOGICAL SPLIT SUMMARY")
    print("=" * 80)

    print("\nTraining dataset:")
    print(
        f"  Rows: {len(train_data):,}"
    )
    print(
        f"  Date range: "
        f"{train_data['week_start'].min()} "
        f"to "
        f"{train_data['week_start'].max()}"
    )

    print("\nValidation dataset:")
    print(
        f"  Rows: {len(validation_data):,}"
    )
    print(
        f"  Date range: "
        f"{validation_data['week_start'].min()} "
        f"to "
        f"{validation_data['week_start'].max()}"
    )

    print("\nTest dataset:")
    print(
        f"  Rows: {len(test_data):,}"
    )
    print(
        f"  Date range: "
        f"{test_data['week_start'].min()} "
        f"to "
        f"{test_data['week_start'].max()}"
    )

    # ------------------------------------------------------------------
    # 6. CHECK FOR OVERLAPPING DATES
    # ------------------------------------------------------------------

    print("\n" + "=" * 80)
    print("CHECKING FOR DATE OVERLAP")
    print("=" * 80)

    train_max = train_data["week_start"].max()
    validation_min = validation_data["week_start"].min()
    validation_max = validation_data["week_start"].max()
    test_min = test_data["week_start"].min()

    print(
        f"\nTraining ends: "
        f"{train_max}"
    )

    print(
        f"Validation starts: "
        f"{validation_min}"
    )

    print(
        f"Validation ends: "
        f"{validation_max}"
    )

    print(
        f"Test starts: "
        f"{test_min}"
    )

    if train_max < validation_min:
        print(
            "\nPASS: Training data comes before validation data."
        )
    else:
        print(
            "\nFAIL: Training and validation dates overlap."
        )

    if validation_max < test_min:
        print(
            "PASS: Validation data comes before test data."
        )
    else:
        print(
            "FAIL: Validation and test dates overlap."
        )

    # ------------------------------------------------------------------
    # 7. FINAL SUMMARY
    # ------------------------------------------------------------------

    print("\n" + "=" * 80)
    print("DATASET SPLIT COMPLETED")
    print("=" * 80)

    print("\nFiles created:")

    print(
        f"  - {train_file}"
    )

    print(
        f"  - {validation_file}"
    )

    print(
        f"  - {test_file}"
    )


if __name__ == "__main__":
    main()