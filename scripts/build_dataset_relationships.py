from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def main():
    print("=" * 80)
    print("DATASET RELATIONSHIP ANALYSIS")
    print("=" * 80)

    users = pd.read_csv(RAW_DATA_DIR / "users.csv")
    teams = pd.read_csv(RAW_DATA_DIR / "teams.csv")
    projects = pd.read_csv(RAW_DATA_DIR / "projects.csv")
    tasks = pd.read_csv(RAW_DATA_DIR / "tasks.csv")
    declarations = pd.read_csv(RAW_DATA_DIR / "declarations.csv")

    print("\nFiles loaded successfully.")

    print(f"\nUsers: {len(users):,}")
    print(f"Teams: {len(teams):,}")
    print(f"Projects: {len(projects):,}")
    print(f"Tasks: {len(tasks):,}")
    print(f"Declarations: {len(declarations):,}")

    print("\n" + "=" * 80)
    print("KEY RELATIONSHIPS")
    print("=" * 80)

    print("\nUsers → Teams")
    print(f"User team IDs: {users['team_id'].nunique():,}")
    print(f"Teams: {teams['id'].nunique():,}")

    print("\nProjects → Teams")
    print(f"Project team IDs: {projects['team_id'].nunique():,}")

    print("\nTasks → Projects")
    print(f"Task project IDs: {tasks['project_id'].nunique():,}")

    print("\nDeclarations → Users")
    print(f"Declaration user IDs: {declarations['user_id'].nunique():,}")

    print("\nDeclarations → Tasks")
    print(f"Declaration task IDs: {declarations['task_id'].nunique():,}")

    print("\n" + "=" * 80)
    print("REFERENTIAL INTEGRITY CHECK")
    print("=" * 80)

    user_ids = set(users["id"])
    team_ids = set(teams["id"])
    project_ids = set(projects["id"])
    task_ids = set(tasks["id"])

    invalid_user_ids = set(declarations["user_id"]) - user_ids
    invalid_task_ids = set(declarations["task_id"]) - task_ids
    invalid_project_ids = set(tasks["project_id"]) - project_ids
    invalid_team_ids = set(projects["team_id"]) - team_ids

    print("\nDeclarations → Users")
    print(f"Invalid user IDs: {len(invalid_user_ids):,}")

    print("\nDeclarations → Tasks")
    print(f"Invalid task IDs: {len(invalid_task_ids):,}")

    print("\nTasks → Projects")
    print(f"Invalid project IDs: {len(invalid_project_ids):,}")

    print("\nProjects → Teams")
    print(f"Invalid team IDs: {len(invalid_team_ids):,}")

    


if __name__ == "__main__":
    main()

   