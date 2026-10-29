from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


# Baseline weekly capacity.
# This will later be replaced by employee-specific capacity.
DEFAULT_WEEKLY_CAPACITY = 40.0


def classify_workload(utilization):

    if utilization < 0.50:
        return "Underutilized"

    elif utilization < 0.80:
        return "Low Workload"

    elif utilization <= 1.00:
        return "Healthy"

    elif utilization <= 1.20:
        return "High Workload"

    else:
        return "Overloaded"


def main():

    print("=" * 80)
    print("EMPLOYEE CAPACITY ANALYSIS")
    print("=" * 80)

    # ---------------------------------------------------------------
    # 1. LOAD FORECAST
    # ---------------------------------------------------------------

    input_file = (
        PROCESSED_DATA_DIR /
        "next_week_workload_forecast.csv"
    )

    print("\nLoading workload forecast...")

    forecast = pd.read_csv(input_file)

    print(
        f"Forecast records: {len(forecast):,}"
    )

    # ---------------------------------------------------------------
    # 2. DEFINE CAPACITY
    # ---------------------------------------------------------------

    print(
        f"\nBaseline weekly capacity: "
        f"{DEFAULT_WEEKLY_CAPACITY} hours"
    )

    forecast["weekly_capacity_hours"] = (
        DEFAULT_WEEKLY_CAPACITY
    )

    # ---------------------------------------------------------------
    # 3. CALCULATE UTILIZATION
    # ---------------------------------------------------------------

    forecast["utilization"] = (
        forecast["predicted_next_week_workload"]
        / forecast["weekly_capacity_hours"]
    )

    forecast["utilization_percentage"] = (
        forecast["utilization"] * 100
    )

    # ---------------------------------------------------------------
    # 4. CALCULATE EXCESS / REMAINING CAPACITY
    # ---------------------------------------------------------------

    forecast["capacity_difference_hours"] = (
        forecast["weekly_capacity_hours"]
        - forecast["predicted_next_week_workload"]
    )

    # ---------------------------------------------------------------
    # 5. CLASSIFY WORKLOAD
    # ---------------------------------------------------------------

    forecast["workload_status"] = (
        forecast["utilization"]
        .apply(classify_workload)
    )

    # ---------------------------------------------------------------
    # 6. SAVE RESULTS
    # ---------------------------------------------------------------

    output_file = (
        PROCESSED_DATA_DIR /
        "employee_capacity_analysis.csv"
    )

    forecast.to_csv(
        output_file,
        index=False
    )

    # ---------------------------------------------------------------
    # 7. DISPLAY SUMMARY
    # ---------------------------------------------------------------

    print("\n" + "=" * 80)
    print("CAPACITY ANALYSIS SUMMARY")
    print("=" * 80)

    status_counts = (
        forecast["workload_status"]
        .value_counts()
    )

    print("\nEmployee workload status:")

    print(status_counts.to_string())

    # ---------------------------------------------------------------
    # 8. DISPLAY OVERLOADED EMPLOYEES
    # ---------------------------------------------------------------

    overloaded = forecast[
        forecast["workload_status"] == "Overloaded"
    ]

    print("\n" + "=" * 80)
    print("OVERLOADED EMPLOYEES")
    print("=" * 80)

    print(
        f"\nNumber of overloaded employees: "
        f"{len(overloaded):,}"
    )

    if not overloaded.empty:

        print(
            overloaded[
                [
                    "user_id",
                    "predicted_next_week_workload",
                    "weekly_capacity_hours",
                    "utilization_percentage",
                    "capacity_difference_hours",
                    "workload_status"
                ]
            ]
            .head(10)
            .to_string(index=False)
        )

    # ---------------------------------------------------------------
    # 9. DISPLAY UNDERUTILIZED EMPLOYEES
    # ---------------------------------------------------------------

    underutilized = forecast[
        forecast["workload_status"] == "Underutilized"
    ]

    print("\n" + "=" * 80)
    print("UNDERUTILIZED EMPLOYEES")
    print("=" * 80)

    print(
        f"\nNumber of underutilized employees: "
        f"{len(underutilized):,}"
    )

    if not underutilized.empty:

        print(
            underutilized[
                [
                    "user_id",
                    "predicted_next_week_workload",
                    "weekly_capacity_hours",
                    "utilization_percentage",
                    "capacity_difference_hours",
                    "workload_status"
                ]
            ]
            .head(10)
            .to_string(index=False)
        )

    print(
        f"\nCapacity analysis saved to: {output_file}"
    )

    print("\n" + "=" * 80)
    print("CAPACITY ANALYSIS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()