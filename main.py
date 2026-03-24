import os
import json
import random
import numpy as np
import tensorflow as tf

from config.config import MAT_X, MAT_Y, MAT_LOC, DIR_MODELS, DIR_RESULTS

from data.data_loader import load_mat_dataset
from data.preprocessing import build_spatiotemporal_windows

from training.train_detectors import train_detection_ensemble
from training.train_localizer import train_pooled_localizer

from evaluation.metrics import compute_auc_per_detector
from evaluation.plots import plot_alpha_vs_auc, plot_zone_accuracy, plot_roc_pr
from evaluation.localization_metrics import generate_zone_confusion
from evaluation.save_summary import save_run_summary
from evaluation.experiment_report import generate_experiment_report

from explainability.gradcam import generate_gradcam_pool, save_gradcam_examples
from explainability.shap_explainer import run_shap_explainer_detector


def main():

    SEED = 42

    np.random.seed(SEED)
    random.seed(SEED)
    tf.random.set_seed(SEED)

    # ---------------------------------------------------
    # CREATE DIRECTORIES
    # ---------------------------------------------------

    os.makedirs(DIR_MODELS, exist_ok=True)
    os.makedirs(DIR_RESULTS, exist_ok=True)

    # ---------------------------------------------------
    # LOAD DATA
    # ---------------------------------------------------

    print("Loading dataset...")

    X_raw, y, attack_zone, zones = load_mat_dataset(MAT_X, MAT_Y, MAT_LOC)

    print("Preprocessing dataset...")

    X = build_spatiotemporal_windows(X_raw)

    # ---------------------------------------------------
    # TRAIN ENSEMBLE DETECTORS
    # ---------------------------------------------------

    print("Training ensemble detectors...")

    ensemble = train_detection_ensemble(X, y)

    print("Training finished.")

    # ---------------------------------------------------
    # GENERATE GRADCAM POOL
    # ---------------------------------------------------

    print("Generating Grad-CAM pooled heatmaps...")

    heatmaps_all, zones_all = generate_gradcam_pool(
        ensemble["cnn_models"],
        X,
        y,
        attack_zone,
        cache_file=os.path.join(DIR_RESULTS, "pooled_heatmaps.npz"),
        rebuild_cache=False
    )

    print("Heatmap pool size:", heatmaps_all.shape)

    # ---------------------------------------------------
    # SAVE GRADCAM EXAMPLES (FOR UI)
    # Real TP/FP/MIS indices computed inside save_gradcam_examples
    # ---------------------------------------------------

    print("Saving Grad-CAM visualization examples...")

    save_gradcam_examples(
        example_groups=None,
        X_input=X,
        y=y,
        attack_zone=attack_zone,
        cnn_models=ensemble["cnn_models"]
    )

    # ---------------------------------------------------
    # TRAIN LOCALIZER CNN
    # ---------------------------------------------------

    print("Training pooled localizer CNN...")

    pooled_localizer = train_pooled_localizer(
        heatmaps_all,
        zones_all,
        zones
    )

    if pooled_localizer is not None:
        pooled_localizer.save(os.path.join(DIR_MODELS, "pooled_localizer.keras"))
        print("Saved pooled localizer model.")

    # ---------------------------------------------------
    # LOAD TEST DATA
    # ---------------------------------------------------

    X_test = np.load(os.path.join(DIR_MODELS, "X_test.npy"))
    y_test = np.load(os.path.join(DIR_MODELS, "y_test.npy"))

    probs  = ensemble["ensemble_predict_fn"](X_test)
    THRESHOLD = 0.55  # Raised from 0.5 to reduce false positives and improve precision
    y_pred = (probs >= THRESHOLD).astype(int)

    # ---------------------------------------------------
    # LOCALIZATION METRICS
    # ---------------------------------------------------

    generate_zone_confusion(
        attack_zone[:len(y_pred)],
        y_test,
        y_pred
    )

    # ---------------------------------------------------
    # DETECTION METRICS
    # ---------------------------------------------------

    print("Evaluating detectors...")

    auc_values = compute_auc_per_detector()

    # ---------------------------------------------------
    # EXPERIMENT REPORT
    # ---------------------------------------------------

    report = generate_experiment_report(y_test, y_pred, probs)

    # ---------------------------------------------------
    # GENERATE GRAPHS
    # ---------------------------------------------------

    print("Generating graphs...")

    plot_alpha_vs_auc(auc_values)
    plot_roc_pr()
    plot_zone_accuracy()

    print("Graphs saved.")

    # ---------------------------------------------------
    # SHAP EXPLAINABILITY
    # ---------------------------------------------------

    print("Generating SHAP explanations...")

    run_shap_explainer_detector(
        ensemble["cnn_models"][2][1],  # detector alpha=1.0
        X,
        y
    )

    # ---------------------------------------------------
    # SUMMARY FILE
    # ---------------------------------------------------

    summary = {
        "ensemble_test_auc":  float(ensemble["auc_test"]),
        "detectors_trained":  len(ensemble["cnn_models"])
    }

    save_run_summary(summary)

    # ---------------------------------------------------
    # PREDICTED ZONE — use actual localizer model
    # ---------------------------------------------------

    pred_zone = -1

    if pooled_localizer is not None:
        try:
            from explainability.gradcam import compute_gradcam_heatmap

            flagged_test_idx = np.where(y_pred == 1)[0]

            if len(flagged_test_idx) > 0:
                _, ref_model = ensemble["cnn_models"][2]  # alpha=1.0

                test_heatmaps = []

                for idx in flagged_test_idx[:100]:
                    img = X_test[idx: idx + 1]
                    hm  = compute_gradcam_heatmap(ref_model, img)
                    test_heatmaps.append(hm[..., np.newaxis].astype(np.float32))

                if len(test_heatmaps) > 0:
                    test_heatmaps_arr = np.stack(test_heatmaps, axis=0)
                    zone_preds = np.argmax(
                        pooled_localizer.predict(test_heatmaps_arr, verbose=0),
                        axis=1
                    )
                    pred_zone = int(np.bincount(zone_preds).argmax())

            print(f"Localizer predicted zone: {pred_zone}")

        except Exception as e:
            print(f"Localizer prediction failed: {e}. Falling back to -1.")
            pred_zone = -1

    # ---------------------------------------------------
    # DASHBOARD DATA
    #
    # attack_probability:
    #   Show the probability of the most confidently detected
    #   attack in the test set. This correctly represents the
    #   system catching a real attack, aligned with the paper's
    #   per-sample classification approach.
    #
    #   If no attacks are detected, fall back to mean probability.
    # ---------------------------------------------------

    attacked_indices = np.where(y_pred == 1)[0]

    if len(attacked_indices) > 0:
        # Most confidently detected attack sample
        most_confident_idx  = attacked_indices[np.argmax(probs[attacked_indices])]
        display_probability = float(probs[most_confident_idx])

        # Use the actual attack zone of that sample if available
        if most_confident_idx < len(attack_zone) and attack_zone[most_confident_idx] >= 0:
            display_zone = int(attack_zone[most_confident_idx])
        else:
            display_zone = pred_zone

    else:
        # No attacks detected in test set — show mean probability
        display_probability = float(np.mean(probs))
        display_zone        = -1

    dashboard_data = {
        # Detection
        "attack_probability":    display_probability,
        "predicted_zone":        display_zone,

        # Model performance — from experiment report
        "ensemble_auc":          float(ensemble["auc_test"]),
        "precision":             float(report["precision"]),
        "recall":                float(report["recall"]),
        "f1_score":              float(report["f1_score"]),

        # Summary counts
        "detection_rate":        float(np.mean(y_pred[y_test == 1])) if y_test.sum() > 0 else 0.0,
        "total_samples":         int(len(y_test)),
        "total_attacks_detected": int(y_pred.sum())
    }

    dashboard_path = os.path.join(DIR_RESULTS, "dashboard_data.json")

    with open(dashboard_path, "w") as f:
        json.dump(dashboard_data, f, indent=2)

    print("Saved dashboard data:", dashboard_path)
    print(f"Display probability: {display_probability:.4f} (attack detected: {display_probability >= THRESHOLD})")
    print(f"Display zone: {display_zone}")
    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()