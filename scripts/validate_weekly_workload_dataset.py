
import os
import pandas as pd


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
    "weekly_employee_workload.csv"
)


# ============================================================
# VALIDATION INITIALIZATION
# ============================================================

print("=" * 60)
print("WEEKLY WORKLOAD DATASET VALIDATION")
print("=" * 60)

if not os.path.exists(DATA_FILE):
    raise FileNotFoundError(
        f"Dataset not found: {DATA_FILE}"
    )

total_rows = 0
total_hours = 0
total_work_logs = 0
total_tasks = 0

missing_values = 0
negative_workloads = 0
duplicate_count = 0
invalid_dates = 0

employees = set()
employee_week_keys = set()

earliest_week = None
latest_week = None
maximum_weekly_hours = 0


# ============================================================
# READ DATASET IN CHUNKS
# ============================================================

print("\nReading weekly workload dataset...")

for chunk in pd.read_csv(
    DATA_FILE,
    chunksize=50000
):

    total_rows += len(chunk)

    # --------------------------------------------------------
    # CHECK MISSING VALUES
    # --------------------------------------------------------

    missing_values += int(
        chunk.isna().sum().sum()
    )

    # --------------------------------------------------------
    # CONVERT NUMERIC COLUMNS
    # --------------------------------------------------------

    chunk["total_workload_hours"] = pd.to_numeric(
        chunk["total_workload_hours"],
        errors="coerce"
    )

    chunk["work_log_count"] = pd.to_numeric(
        chunk["work_log_count"],
        errors="coerce"
    )

    chunk["unique_tasks"] = pd.to_numeric(
        chunk["unique_tasks"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # CALCULATE TOTALS
    # --------------------------------------------------------

    total_hours += chunk[
        "total_workload_hours"
    ].sum()

    total_work_logs += chunk[
        "work_log_count"
    ].sum()

    total_tasks += chunk[
        "unique_tasks"
    ].sum()

    # --------------------------------------------------------
    # CHECK NEGATIVE WORKLOADS
    # --------------------------------------------------------

    negative_workloads += int(
        (chunk["total_workload_hours"] < 0).sum()
    )

    # --------------------------------------------------------
    # CHECK EMPLOYEE-WEEK DUPLICATES
    # --------------------------------------------------------

    chunk["week_start"] = pd.to_datetime(
        chunk["week_start"],
        errors="coerce"
    )

    invalid_dates += int(
        chunk["week_start"].isna().sum()
    )

    valid_rows = chunk.dropna(
        subset=["employee_id", "week_start"]
    )

    for employee_id, week_start in zip(
        valid_rows["employee_id"],
        valid_rows["week_start"]
    ):

        key = (
            str(employee_id),
            week_start
        )

        if key in employee_week_keys:
            duplicate_count += 1

        else:
            employee_week_keys.add(key)

    # --------------------------------------------------------
    # COUNT UNIQUE EMPLOYEES
    # --------------------------------------------------------

    employees.update(
        chunk["employee_id"].dropna().astype(str).unique()
    )

    # --------------------------------------------------------
    # FIND DATE RANGE
    # --------------------------------------------------------

    chunk_min = chunk["week_start"].min()
    chunk_max = chunk["week_start"].max()

    if pd.notna(chunk_min):

        if earliest_week is None or chunk_min < earliest_week:
            earliest_week = chunk_min

    if pd.notna(chunk_max):

        if latest_week is None or chunk_max > latest_week:
            latest_week = chunk_max

    # --------------------------------------------------------
    # FIND MAXIMUM WEEKLY WORKLOAD
    # --------------------------------------------------------

    chunk_max_hours = chunk[
        "total_workload_hours"
    ].max()

    if pd.notna(chunk_max_hours):

        maximum_weekly_hours = max(
            maximum_weekly_hours,
            chunk_max_hours
        )

    print(
        f"Validated {total_rows:,} records..."
    )


# ============================================================
# DISPLAY FINAL VALIDATION RESULTS
# ============================================================

print("\n" + "=" * 60)
print("VALIDATION RESULTS")
print("=" * 60)

print(
    f"Total weekly records: {total_rows:,}"
)

print(
    f"Unique employees: {len(employees):,}"
)

print(
    f"Duplicate employee-week combinations: {duplicate_count:,}"
)

print(
    f"Missing values: {missing_values:,}"
)

print(
    f"Invalid week dates: {invalid_dates:,}"
)

print(
    f"Negative workload records: {negative_workloads:,}"
)

print(
    f"Total workload hours: {total_hours:,.2f}"
)

print(
    f"Total work logs represented: {total_work_logs:,}"
)

print(
    f"Total task counts across weeks: {total_tasks:,}"
)

print(
    f"Earliest week: {earliest_week}"
)

print(
    f"Latest week: {latest_week}"
)

print(
    f"Maximum weekly workload: {maximum_weekly_hours:,.2f}"
)


# ============================================================
# FINAL VALIDATION STATUS
# ============================================================

print("\n" + "=" * 60)

if (
    duplicate_count == 0
    and missing_values == 0
    and invalid_dates == 0
    and negative_workloads == 0
):

    print("VALIDATION PASSED")

else:

    print("VALIDATION NEEDS ATTENTION")

print("=" * 60)
