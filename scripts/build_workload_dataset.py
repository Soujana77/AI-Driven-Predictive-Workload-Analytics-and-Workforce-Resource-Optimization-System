from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


def main():
    print("=" * 80)
    print("BUILD HISTORICAL WORKLOAD DATASET")
    print("=" * 80)

    print("\nLoading datasets...")

    users = pd.read_csv(
        RAW_DATA_DIR / "users.csv",
        usecols=["id", "team_id"]
    )

    tasks = pd.read_csv(
        RAW_DATA_DIR / "tasks.csv",
        usecols=["id", "project_id"]
    )

    projects = pd.read_csv(
        RAW_DATA_DIR / "projects.csv",
        usecols=["id", "team_id"]
    )

    declarations = pd.read_csv(
        RAW_DATA_DIR / "declarations.csv",
        usecols=[
            "date",
            "duration",
            "user_id",
            "task_id"
        ]
    )

    print("Datasets loaded successfully.")

    print("\nConverting date...")

    declarations["date"] = pd.to_datetime(
        declarations["date"],
        errors="coerce"
    )

    print("\nConverting duration to hours...")

    declarations["duration_hours"] = (
        declarations["duration"]
        / 1_000_000_000
        / 3600
    )

    print("\nCleaning invalid records...")

    initial_count = len(declarations)

    declarations = declarations.dropna(
        subset=["date"]
    )

    declarations = declarations[
        declarations["duration_hours"] >= 0
    ]

    cleaned_count = len(declarations)

    print(f"Initial records: {initial_count:,}")
    print(f"Removed records: {initial_count - cleaned_count:,}")
    print(f"Remaining records: {cleaned_count:,}")

    print("\nFlagging extreme durations...")

    declarations["is_extreme_duration"] = (
        declarations["duration_hours"] > 100
    )

    print(
        "Extreme duration records:",
        declarations["is_extreme_duration"].sum()
    )

    print("\nJoining users...")

    workload = declarations.merge(
        users,
        left_on="user_id",
        right_on="id",
        how="left"
    )

    workload = workload.rename(
        columns={"team_id": "user_team_id"}
    )

    workload = workload.drop(
        columns=["id"]
    )

    print("Joining tasks...")

    workload = workload.merge(
        tasks,
        left_on="task_id",
        right_on="id",
        how="left"
    )

    workload = workload.drop(
        columns=["id"]
    )

    print("Joining projects...")

    workload = workload.merge(
        projects,
        left_on="project_id",
        right_on="id",
        how="left"
    )

    workload = workload.rename(
        columns={"team_id": "project_team_id"}
    )

    workload = workload.drop(
        columns=["id"]
    )

    workload = workload[
        [
            "date",
            "user_id",
            "user_team_id",
            "project_id",
            "project_team_id",
            "task_id",
            "duration_hours",
            "is_extreme_duration"
        ]
    ]

    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        PROCESSED_DATA_DIR /
        "historical_workload.csv"
    )

    workload.to_csv(
        output_file,
        index=False
    )

    print("\n" + "=" * 80)
    print("DATASET CREATED")
    print("=" * 80)

    print(f"\nRows: {len(workload):,}")
    print(f"Columns: {len(workload.columns)}")

    print("\nDate range:")
    print(
        f"  {workload['date'].min()} "
        f"to "
        f"{workload['date'].max()}"
    )

    print("\nTotal workload hours:")
    print(
        f"  {workload['duration_hours'].sum():,.2f}"
    )

    print("\nExtreme records:")
    print(
        f"  {workload['is_extreme_duration'].sum():,}"
    )

    print("\nSaved to:")
    print(f"  {output_file}")

    print("\n" + "=" * 80)
    print("WORKLOAD DATASET BUILD COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()