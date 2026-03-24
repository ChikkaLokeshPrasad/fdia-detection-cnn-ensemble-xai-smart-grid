import json
import os
import numpy as np
from sklearn.metrics import (
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

from config.config import DIR_RESULTS


def generate_experiment_report(y_true, y_pred, probs):

    report = {}

    report["auc"] = float(roc_auc_score(y_true, probs))
    report["precision"] = float(precision_score(y_true, y_pred))
    report["recall"] = float(recall_score(y_true, y_pred))
    report["f1_score"] = float(f1_score(y_true, y_pred))

    cm = confusion_matrix(y_true, y_pred)

    report["confusion_matrix"] = cm.tolist()

    os.makedirs(DIR_RESULTS, exist_ok=True)

    path = os.path.join(DIR_RESULTS, "experiment_report.json")

    with open(path, "w") as f:
        json.dump(report, f, indent=2)

    print("Saved experiment report to:", path)

    return report