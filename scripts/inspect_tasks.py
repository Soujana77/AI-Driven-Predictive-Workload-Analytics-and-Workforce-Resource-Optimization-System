import os
import pandas as pd


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

TASKS_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "raw",
    "tasks.csv"
)


print("Loading tasks dataset...")

tasks = pd.read_csv(TASKS_FILE)

print("\n========== TASK DATASET ==========")

print(f"Rows: {len(tasks):,}")
print(f"Columns: {len(tasks.columns)}")

print("\nColumn names:")
print(tasks.columns.tolist())

print("\nData types:")
print(tasks.dtypes)

print("\nFirst 5 rows:")
print(tasks.head())

print("\nMissing values:")
print(tasks.isnull().sum())

print("\nUnique values:")
for column in tasks.columns:
    print(
        f"{column}: {tasks[column].nunique(dropna=True):,}"
    )