from pathlib import Path
import pandas as pd


# Find the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Location of the raw dataset
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def inspect_csv(file_path):
    """Inspect one CSV file without loading the entire file."""

    print("\n" + "=" * 80)
    print(f"FILE: {file_path.name}")
    print("=" * 80)

    try:
        # Read only the first 5 rows.
        # This is important because some of our CSV files are very large.
        df = pd.read_csv(file_path, nrows=5)

        print(f"\nNumber of columns: {len(df.columns)}")

        print("\nColumns:")
        for column in df.columns:
            print(f"  - {column}")

        print("\nData types:")
        print(df.dtypes.to_string())

        print("\nFirst 5 rows:")
        print(df.to_string(index=False))

    except Exception as error:
        print(f"\nCould not read {file_path.name}")
        print(f"Error: {error}")


def main():
    """Find and inspect all CSV files in data/raw."""

    print("AI WORKLOAD FORECAST AND PLANNING ASSISTANT")
    print("RAW DATASET INSPECTION")
    print("=" * 80)

    # Check whether the raw data folder exists
    if not RAW_DATA_DIR.exists():
        print(f"\nERROR: Raw data folder not found:")
        print(RAW_DATA_DIR)
        return

    # Find all CSV files
    csv_files = sorted(RAW_DATA_DIR.glob("*.csv"))

    if not csv_files:
        print("\nERROR: No CSV files found in data/raw/")
        return

    print(f"\nFound {len(csv_files)} CSV files.")

    print("\nFiles found:")
    for file in csv_files:
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"  - {file.name} ({size_mb:.2f} MB)")

    # Inspect every CSV
    for csv_file in csv_files:
        inspect_csv(csv_file)

    print("\n" + "=" * 80)
    print("DATASET INSPECTION COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()