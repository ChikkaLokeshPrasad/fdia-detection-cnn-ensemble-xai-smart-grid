import os
import csv
import numpy as np

from config.config import DIR_RESULTS


def generate_zone_confusion(attack_zone, y_true, y_pred):

    # Filter out zone -1 (normal samples with no attack location)
    zones = [z for z in np.unique(attack_zone) if z >= 0]

    if len(zones) == 0:
        print("No valid attack zones found. Skipping zone confusion matrix.")
        return

    results = []

    for zid in zones:

        zone_mask    = attack_zone == zid
        attack_mask  = y_true == 1

        total_attacks = int(np.sum(zone_mask & attack_mask))

        if total_attacks == 0:
            continue

        detected = [
            i for i in np.where(zone_mask)[0]
            if y_pred[i] == 1
        ]

        correct_localizations = sum(
            1 for i in detected if attack_zone[i] == zid
        )

        results.append({
            "zone":                   int(zid),
            "total_attacks":          total_attacks,
            "detected":               len(detected),
            "correct_localizations":  correct_localizations
        })

    os.makedirs(DIR_RESULTS, exist_ok=True)

    csv_path = os.path.join(DIR_RESULTS, "per_zone_confusion.csv")

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "zone",
                "total_attacks",
                "detected",
                "correct_localizations"
            ],
        )
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    print(f"Saved per-zone metrics to: {csv_path}")
    print(f"Zones covered: {[r['zone'] for r in results]}")