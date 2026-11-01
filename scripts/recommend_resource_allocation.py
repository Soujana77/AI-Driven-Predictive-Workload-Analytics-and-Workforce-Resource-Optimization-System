from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


def main():

    print("=" * 80)
    print("RESOURCE RECOMMENDATION")
    print("=" * 80)

    input_file = (
        PROCESSED_DATA_DIR /
        "employee_capacity_analysis.csv"
    )

    output_file = (
        PROCESSED_DATA_DIR /
        "resource_recommendations.csv"
    )

    data = pd.read_csv(input_file)

    # Employees with available capacity
    available = data[
        data["utilization"] < 0.80
    ].copy()

    overloaded = data[
        data["utilization"] > 1.00
    ].copy()

    recommendations = []

    for _, overloaded_employee in overloaded.iterrows():

        for _, available_employee in available.iterrows():

            available_capacity = (
                available_employee["weekly_capacity_hours"]
                - available_employee[
                    "predicted_next_week_workload"
                ]
            )

            if available_capacity <= 0:
                continue

            # Higher available capacity = better candidate
            capacity_score = min(
                available_capacity / 40,
                1.0
            )

            # Lower workload = better candidate
            workload_score = max(
                0,
                1 - available_employee["utilization"]
            )

            score = (
                0.6 * capacity_score
                + 0.4 * workload_score
            )

            recommendations.append({
                "overloaded_employee": overloaded_employee["user_id"],
                "recommended_employee": available_employee["user_id"],
                "overloaded_workload": overloaded_employee[
                    "predicted_next_week_workload"
                ],
                "recommended_employee_workload": available_employee[
                    "predicted_next_week_workload"
                ],
                "available_capacity_hours": available_capacity,
                "recommendation_score": score
            })

    recommendations = pd.DataFrame(
        recommendations
    )

    if not recommendations.empty:

        recommendations = recommendations.sort_values(
            [
                "overloaded_employee",
                "recommendation_score"
            ],
            ascending=[True, False]
        )

        recommendations["rank"] = (
            recommendations
            .groupby("overloaded_employee")
            .cumcount()
            + 1
        )

        recommendations = recommendations[
            recommendations["rank"] <= 5
        ]

    recommendations.to_csv(
        output_file,
        index=False
    )

    print(
        f"\nOverloaded employees: {len(overloaded):,}"
    )

    print(
        f"Available employees: {len(available):,}"
    )

    print(
        f"Recommendations generated: "
        f"{len(recommendations):,}"
    )

    print("\nTop recommendations:")

    if not recommendations.empty:
        print(
            recommendations.head(20)
            .to_string(index=False)
        )

    print(
        f"\nSaved to: {output_file}"
    )


if __name__ == "__main__":
    main()