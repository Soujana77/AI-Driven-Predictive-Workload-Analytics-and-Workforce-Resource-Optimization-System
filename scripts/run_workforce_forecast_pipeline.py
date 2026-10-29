from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent


SCRIPTS = [
    "build_forecasting_features.py",
    "split_forecasting_dataset.py",
    "train_baseline_model.py",
    "train_random_forest_model.py",
    "compare_forecasting_models.py",
    "analyze_feature_importance.py",
    "predict_next_week_workload.py",
    "analyze_employee_capacity.py",
    "detect_workload_risks.py",
    "recommend_resource_allocation.py",
]


def main():

    print("=" * 80)
    print("WORKFORCE FORECASTING PIPELINE")
    print("=" * 80)

    for script in SCRIPTS:

        print("\n" + "=" * 80)
        print(f"RUNNING: {script}")
        print("=" * 80)

        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / script)
            ]
        )

        if result.returncode != 0:

            print(
                f"\nPipeline stopped because {script} failed."
            )

            sys.exit(result.returncode)

    print("\n" + "=" * 80)
    print("COMPLETE WORKFORCE PIPELINE FINISHED")
    print("=" * 80)


if __name__ == "__main__":
    main()