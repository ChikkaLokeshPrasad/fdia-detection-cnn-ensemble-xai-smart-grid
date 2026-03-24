import os
import numpy as np
import matplotlib.pyplot as plt

from config.config import DIR_RESULTS

DIR_SHAP = os.path.join(DIR_RESULTS, "shap")


# ---------------------------
# SHAP explainability
# ---------------------------
def run_shap_explainer_detector(
    model, X, y, out_dir=DIR_SHAP, tag="detector_alpha_1.0"
):
    """
    Compute SHAP explanations for one detector CNN.
    Saves numpy SHAP values and a simple per-bus importance bar plot.
    """
    try:
        import shap
    except ImportError:
        print("SHAP is not installed; skipping SHAP explanations.")
        return

    os.makedirs(out_dir, exist_ok=True)

    # choose background from normal samples if available
    idx_bg = np.where(y == 0)[0]
    if idx_bg.size == 0:
        idx_bg = np.arange(len(y))
    bg_size = min(100, idx_bg.size)
    idx_bg = np.random.choice(idx_bg, bg_size, replace=False)
    background = X[idx_bg]

    # choose some attacked samples for explanation
    idx_explain = np.where(y == 1)[0]
    if idx_explain.size == 0:
        idx_explain = np.arange(len(y))
    explain_size = min(200, idx_explain.size)
    idx_explain = np.random.choice(idx_explain, explain_size, replace=False)
    X_explain = X[idx_explain]

    print(
        f"Running SHAP for {tag}: background={len(background)}, explain={len(X_explain)}"
    )

    explainer = shap.GradientExplainer(model, background)
    shap_values = explainer.shap_values(X_explain)[0]  # binary -> first output

    np.save(
        os.path.join(out_dir, f"{tag}_shap_values.npy"),
        shap_values,
    )
    np.save(
        os.path.join(out_dir, f"{tag}_samples_idx.npy"),
        idx_explain,
    )

    # Aggregate over time and channel to get per-bus importance
    # shap_values shape: (N, H, W, C)
    bus_importance = np.mean(np.abs(shap_values), axis=(0, 2, 3))  # (H,)

    plt.figure(figsize=(8, 4))
    plt.bar(np.arange(bus_importance.shape[0]), bus_importance)
    plt.xlabel("Bus index")
    plt.ylabel("Mean |SHAP|")
    plt.title(f"Per-bus importance ({tag})")
    plt.tight_layout()
    out_fig = os.path.join(out_dir, f"{tag}_bus_importance.png")
    plt.savefig(out_fig)
    plt.close()
    print("Saved SHAP explanations to", out_dir)
