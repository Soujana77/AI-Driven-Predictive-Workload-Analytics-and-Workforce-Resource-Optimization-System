import os
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

load_dotenv(
    os.path.join(PROJECT_ROOT, "backend", ".env")
)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL not found in backend/.env"
    )


PROJECTS_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "raw",
    "projects.csv"
)

print("Loading projects dataset...")

projects = pd.read_csv(PROJECTS_FILE)

print(f"Projects loaded: {len(projects):,}")


projects = projects[
    ["id", "created_at", "team_id"]
].copy()


projects["created_at"] = pd.to_datetime(
    projects["created_at"],
    format="mixed",
    utc=True
)


print("\nPrepared project records:")
print(projects.head())


print("\nConnecting to PostgreSQL...")

engine = create_engine(DATABASE_URL)


with engine.begin() as connection:

    projects.to_sql(
        "projects",
        connection,
        if_exists="append",
        index=False
    )


print("\nProjects imported successfully!")
print(f"Records inserted: {len(projects):,}")