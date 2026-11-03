import os
import pandas as pd


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DECLARATIONS_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "raw",
    "declarations.csv"
)


print("Loading declarations dataset...")

declarations = pd.read_csv(
    DECLARATIONS_FILE
)

print("\n========== DECLARATIONS DATASET ==========")

print(f"Rows: {len(declarations):,}")
print(f"Columns: {len(declarations.columns)}")

print("\nColumn names:")
print(declarations.columns.tolist())

print("\nData types:")
print(declarations.dtypes)

print("\nFirst 5 rows:")
print(declarations.head())

print("\nMissing values:")
print(declarations.isnull().sum())

print("\nUnique values:")
for column in declarations.columns:
    print(
        f"{column}: "
        f"{declarations[column].nunique(dropna=True):,}"
    )