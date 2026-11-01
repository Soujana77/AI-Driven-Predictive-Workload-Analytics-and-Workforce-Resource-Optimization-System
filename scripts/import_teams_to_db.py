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


TEAMS_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "raw",
    "teams.csv"
)


print("Loading teams dataset...")

teams = pd.read_csv(TEAMS_FILE)

print(f"Teams loaded: {len(teams):,}")


# Keep only the fields available in the source dataset

teams = teams[
    [
        "id",
        "created_at",
        "deleted_at"
    ]
]


# Convert timestamps

teams["created_at"] = pd.to_datetime(
    teams["created_at"],
    format="mixed",
    utc=True
)

teams["deleted_at"] = pd.to_datetime(
    teams["deleted_at"],
    format="mixed",
    utc=True
)


print("\nPrepared team records:")
print(teams.head())


print("\nConnecting to PostgreSQL...")

engine = create_engine(DATABASE_URL)

with engine.begin() as connection:

    teams.to_sql(
        "teams",
        connection,
        if_exists="append",
        index=False
    )


print("\nTeams imported successfully!")
print(f"Records inserted: {len(teams):,}")