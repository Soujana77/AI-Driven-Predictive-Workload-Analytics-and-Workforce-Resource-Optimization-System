from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def main():
    print("=" * 80)
    print("FUTURE RECORD INVESTIGATION")
    print("=" * 80)

    file_path = RAW_DATA_DIR / "declarations.csv"

    print("\nLoading declaration dates...")

    declarations = pd.read_csv(
        file_path,
        usecols=[
            "created_at",
            "date",
            "duration",
            "user_id",
            "task_id"
        ]
    )

    print("Dataset loaded successfully.")

    print("\nConverting dates...")

    declarations["date"] = pd.to_datetime(
        declarations["date"],
        errors="coerce"
    )

    declarations["created_at"] = pd.to_datetime(
        declarations["created_at"],
        errors="coerce"
    )

    declarations["date_year"] = (
        declarations["date"].dt.year
    )

    print("\n" + "=" * 80)
    print("DATE VS CREATED_AT")
    print("=" * 80)

    future_records = declarations[
        declarations["date_year"] >= 2025
    ].copy()

    print(
        f"\nRecords from 2025 onward: "
        f"{len(future_records):,}"
    )

    print("\nSample records:")

    print(
        future_records.head(20).to_string(
            index=False
        )
    )

    print("\n" + "=" * 80)
    print("DATE RANGE OF FUTURE-LOOKING RECORDS")
    print("=" * 80)

    print(
        f"\nWork date minimum: "
        f"{future_records['date'].min()}"
    )

    print(
        f"Work date maximum: "
        f"{future_records['date'].max()}"
    )

    print(
        f"\nCreated-at minimum: "
        f"{future_records['created_at'].min()}"
    )

    print(
        f"Created-at maximum: "
        f"{future_records['created_at'].max()}"
    )

    print("\n" + "=" * 80)
    print("YEAR COMPARISON")
    print("=" * 80)

    future_records["created_year"] = (
        future_records["created_at"].dt.year
    )

    comparison = (
        future_records
        .groupby(["date_year", "created_year"])
        .size()
        .reset_index(name="records")
        .sort_values(
            ["date_year", "created_year"]
        )
    )

    print(
        comparison.to_string(
            index=False
        )
    )

    print("\n" + "=" * 80)
    print("FUTURE RECORD INVESTIGATION COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()