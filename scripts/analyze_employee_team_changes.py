from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


def main():
    print("=" * 80)
    print("EMPLOYEE TEAM STABILITY ANALYSIS")
    print("=" * 80)

    file_path = (
        PROCESSED_DATA_DIR /
        "employee_weekly_workload.csv"
    )

    print("\nLoading employee weekly workload...")

    workload = pd.read_csv(
        file_path,
        parse_dates=["week_start"]
    )

    print("Dataset loaded successfully.")

    print("\nCounting teams used by each employee...")

    team_counts = (
        workload
        .groupby("user_id")["user_team_id"]
        .nunique()
    )

    print("\n" + "=" * 80)
    print("TEAM COUNT PER EMPLOYEE")
    print("=" * 80)

    print(
        team_counts.describe()
    )

    print("\nEmployees with exactly one team:")

    one_team = (
        team_counts == 1
    ).sum()

    print(f"  {one_team:,}")

    print("\nEmployees with multiple teams:")

    multiple_teams = (
        team_counts > 1
    ).sum()

    print(f"  {multiple_teams:,}")

    print("\n" + "=" * 80)
    print("EMPLOYEES WITH MULTIPLE TEAMS")
    print("=" * 80)

    employees_multiple_teams = (
        team_counts[
            team_counts > 1
        ]
        .sort_values(
            ascending=False
        )
        .head(20)
    )

    print(
        employees_multiple_teams.to_string()
    )

    print("\n" + "=" * 80)
    print("TEAM STABILITY ANALYSIS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()
    