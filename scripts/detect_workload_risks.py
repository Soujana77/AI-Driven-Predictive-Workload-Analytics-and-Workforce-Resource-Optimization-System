from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"


def determine_risk(row):

    utilization = row["utilization"]

    if utilization > 1.50:
        return "Critical"

    if utilization > 1.20:
        return "High"

    if utilization > 1.00:
        return "Medium"

    if utilization < 0.50:
        return "Low Utilization"

    return "Normal"


def main():

    print("=" * 80)
    print("WORKLOAD RISK DETECTION")
    print("=" * 80)

    input_file = (
        PROCESSED_DATA_DIR /
        "employee_capacity_analysis.csv"
    )

    output_file = (
        PROCESSED_DATA_DIR /
        "workload_risk_analysis.csv"
    )

    data = pd.read_csv(input_file)

    print(f"\nRecords analysed: {len(data):,}")

    data["risk_level"] = data.apply(
        determine_risk,
        axis=1
    )

    data["risk_reason"] = ""

    data.loc[
        data["utilization"] > 1.20,
        "risk_reason"
    ] = "Predicted workload exceeds employee capacity"

    data.loc[
        data["utilization"] > 1.50,
        "risk_reason"
    ] = "Severe workload overload"

    data.loc[
        data["utilization"] < 0.50,
        "risk_reason"
    ] = "Employee has significant available capacity"

    data.to_csv(
        output_file,
        index=False
    )

    print("\nRisk summary:")

    print(
        data["risk_level"]
        .value_counts()
        .to_string()
    )

    print("\nHigh/Critical risks:")

    risks = data[
        data["risk_level"].isin(
            ["High", "Critical"]
        )
    ]

    print(
        risks[
            [
                "user_id",
                "predicted_next_week_workload",
                "weekly_capacity_hours",
                "utilization_percentage",
                "risk_level",
                "risk_reason"
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

    print(
        f"\nSaved to: {output_file}"
    )


if __name__ == "__main__":
    main()
    