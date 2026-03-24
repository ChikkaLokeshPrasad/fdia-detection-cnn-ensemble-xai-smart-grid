import json
import os

from config.config import DIR_RESULTS


def save_run_summary(summary_dict):

    os.makedirs(DIR_RESULTS, exist_ok=True)

    path = os.path.join(DIR_RESULTS, "run_summary.json")

    with open(path, "w") as f:
        json.dump(summary_dict, f, indent=2)

    print("Saved summary to", path)