import os
import pandas as pd

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

PROJECTS_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "raw",
    "projects.csv"
)

print("Loading projects dataset...")

projects = pd.read_csv(PROJECTS_FILE)

print("\n========== PROJECT DATASET ==========")

print(f"Rows: {len(projects):,}")
print(f"Columns: {len(projects.columns)}")

print("\nColumn names:")
print(projects.columns.tolist())

print("\nData types:")
print(projects.dtypes)

print("\nFirst 5 rows:")
print(projects.head())

print("\nMissing values:")
print(projects.isnull().sum())

print("\nUnique values:")
for column in projects.columns:
    print(
        f"{column}: {projects[column].nunique(dropna=True):,}"
    )