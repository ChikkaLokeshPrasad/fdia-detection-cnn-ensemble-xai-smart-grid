import os
import numpy as np
import cv2
import tensorflow as tf
import traceback

from tensorflow.keras import layers

from config.config import MODEL_CONFIG, DIR_RESULTS

DIR_GRADCAM_EX = os.path.join(DIR_RESULTS, "gradcam_examples")


# ---------------------------
# Grad-CAM
# ---------------------------
def compute_gradcam_heatmap(model, img, last_conv_layer_name=None):
    """
    Compute Grad-CAM heatmap for a single input (img shape: (1,H,W,C)).
    Returns 2D heatmap (H,W) in [0,1].
    """
    if last_conv_layer_name is None:
        for layer in reversed(model.layers):
            if isinstance(layer, layers.Conv2D):
                last_conv_layer_name = layer.name
                break

    if last_conv_layer_name is None:
        raise ValueError("No Conv2D layer found for Grad-CAM")

    grad_model = tf.keras.models.Model(
        [model.inputs],
        [model.get_layer(last_conv_layer_name).output, model.output],
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img)
        loss = predictions[:, 0]

    grads = tape.gradient(loss, conv_outputs)
    weights = tf.reduce_mean(grads, axis=(1, 2))  # (1, channels)

    cam = tf.zeros_like(conv_outputs[0, :, :, 0], dtype=tf.float32)

    for i in range(conv_outputs.shape[-1]):
        cam += weights[0, i] * conv_outputs[0, :, :, i]

    cam = tf.nn.relu(cam)
    heatmap = cam.numpy()

    if heatmap.max() > 0:
        heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min())
    else:
        heatmap = np.zeros_like(heatmap)

    # resize to input HxW
    h_in, w_in = img.shape[1], img.shape[2]
    heatmap = cv2.resize(heatmap, (w_in, h_in))

    return heatmap


def _get_example_indices(cnn_models, X_input, y, n=5):
    """
    Use the alpha=1.0 detector (index 2) to compute real
    TP, FP, and misclassification (FN) indices.
    Falls back to the first available model if index 2 is missing.
    """
    model_idx = min(2, len(cnn_models) - 1)
    _, model = cnn_models[model_idx]

    probs = model.predict(X_input, verbose=0).ravel()
    y_pred = (probs >= 0.5).astype(int)
    y_true = y.astype(int)

    tp_idx  = np.where((y_pred == 1) & (y_true == 1))[0]
    fp_idx  = np.where((y_pred == 1) & (y_true == 0))[0]
    fn_idx  = np.where((y_pred == 0) & (y_true == 1))[0]  # misclassifications

    tp_idx  = tp_idx[:n].tolist()
    fp_idx  = fp_idx[:n].tolist()
    mis_idx = fn_idx[:n].tolist()

    print(f"GradCAM examples — TP: {len(tp_idx)}, FP: {len(fp_idx)}, MIS: {len(mis_idx)}")

    return tp_idx, fp_idx, mis_idx


def save_gradcam_examples(
    example_groups, X_input, y, attack_zone, cnn_models, out_dir=DIR_GRADCAM_EX
):
    """
    Saves Grad-CAM overlay images for TP, FP, and misclassified samples.

    example_groups is accepted for backwards compatibility but is ignored.
    Real TP/FP/MIS indices are computed internally from model predictions.
    """

    # Always compute real indices — ignore whatever was passed in
    tp_idx, fp_idx, mis_idx = _get_example_indices(cnn_models, X_input, y, n=5)

    def overlay_and_save(idx, fname_prefix):
        if not (0 <= idx < len(X_input)):
            return

        sample_img = X_input[idx: idx + 1]
        base = sample_img[0, ..., 0]

        bmin, bmax = base.min(), base.max()
        denom = (bmax - bmin) if (bmax - bmin) > 1e-9 else 1.0
        base_vis = (255 * (base - bmin) / denom).astype(np.uint8)

        # Upscale small inputs so the saved image is readable
        scale = max(1, 20 // min(base.shape))
        h_up = base.shape[0] * scale
        w_up = base.shape[1] * scale
        base_vis_up = cv2.resize(base_vis, (w_up, h_up), interpolation=cv2.INTER_NEAREST)
        base_vis_up = cv2.cvtColor(base_vis_up, cv2.COLOR_GRAY2BGR)

        cols = len(cnn_models)
        canvas = np.ones((h_up, w_up * cols, 3), dtype=np.uint8) * 255

        for i, (alpha, model) in enumerate(cnn_models):
            try:
                pred_val = float(model.predict(sample_img, verbose=0).ravel()[0])
            except Exception:
                pred_val = None

            hm = compute_gradcam_heatmap(model, sample_img)
            hm_up = cv2.resize(hm, (w_up, h_up), interpolation=cv2.INTER_LINEAR)
            hm_vis = (255 * hm_up).astype(np.uint8)
            hm_color = cv2.applyColorMap(hm_vis, cv2.COLORMAP_JET)

            overlay = cv2.addWeighted(base_vis_up, 0.6, hm_color, 0.4, 0)

            txt = f"a={alpha}"
            if pred_val is not None:
                txt += f" p={pred_val:.2f}"

            cv2.putText(
                overlay,
                txt,
                (4, 14),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            canvas[:, i * w_up: (i + 1) * w_up, :] = overlay

        zone_val = int(attack_zone[idx]) if (attack_zone is not None and idx < len(attack_zone)) else -1

        fname = os.path.join(
            out_dir,
            f"{fname_prefix}_idx{idx}_zone{zone_val}_y{int(y[idx])}.png",
        )

        cv2.imwrite(fname, canvas)

    os.makedirs(out_dir, exist_ok=True)

    for idx in tp_idx:
        overlay_and_save(idx, "TP")

    for idx in fp_idx:
        overlay_and_save(idx, "FP")

    for idx in mis_idx:
        overlay_and_save(idx, "MIS")

    print(f"Saved Grad-CAM examples to {out_dir}")


# ---------------------------
# Generate pooled Grad-CAM heatmaps
# ---------------------------
def generate_gradcam_pool(
    cnn_models, X, y, attack_zone, cfg=MODEL_CONFIG, cache_file=None, rebuild_cache=False
):
    if cache_file and os.path.exists(cache_file) and not rebuild_cache:
        try:
            data = np.load(cache_file, allow_pickle=True)
            keys = list(data.files)
            print("Cache keys found in", cache_file, "->", keys)

            if "heatmaps_all" in keys and "zones_all" in keys:
                heatmaps_all = data["heatmaps_all"]
                zones_all = data["zones_all"]
                print("Loaded cached pooled heatmaps:", heatmaps_all.shape)
                return heatmaps_all, zones_all

            if len(keys) >= 2:
                cand0 = data[keys[0]]
                cand1 = data[keys[1]]
                if cand0.ndim == 4 and cand1.ndim == 1:
                    print("Loaded cached pooled heatmaps from keys:", keys[0], keys[1])
                    return cand0, cand1
                if cand1.ndim == 4 and cand0.ndim == 1:
                    print("Loaded cached pooled heatmaps from keys:", keys[1], keys[0])
                    return cand1, cand0

            print("Cache exists but format unexpected; will rebuild.")

        except Exception as e:
            print("Failed to load cache:", cache_file, "error:", e)
            traceback.print_exc()
            print("Will rebuild pooled heatmaps now.")

    pooled_heatmaps = []
    pooled_zones = []
    N = X.shape[0]
    bs = int(cfg.get("batch_size", 32))

    for alpha, model in cnn_models:
        print(f"alpha={alpha}: computing Grad-CAM pool candidates")

        try:
            probs = model.predict(X, batch_size=bs, verbose=0).ravel()
        except Exception as e:
            print("Warning: model.predict failed for alpha", alpha, e)
            probs = np.zeros((N,), dtype=float)

        flagged_idx = np.where((probs >= 0.5) & (y == 1))[0]
        print(f"alpha={alpha}: flagged {len(flagged_idx)} samples for pooling")

        for idx in flagged_idx:
            try:
                img = X[idx: idx + 1]
                hm = compute_gradcam_heatmap(model, img)
                hm = np.asarray(hm)

                if hm.ndim != 2:
                    print("Unexpected heatmap ndim:", hm.shape, "for idx", idx)
                    continue

                hm = hm[..., np.newaxis].astype(np.float32)
                pooled_heatmaps.append(hm)

                zone_val = (
                    int(attack_zone[idx])
                    if (attack_zone is not None and idx < len(attack_zone))
                    else -1
                )
                pooled_zones.append(zone_val)

            except Exception as e:
                print("Error computing Grad-CAM for idx", idx, "alpha", alpha, e)
                traceback.print_exc()
                continue

    if len(pooled_heatmaps) == 0:
        print("No pooled heatmaps; returning empty arrays.")
        empty_heatmaps = np.zeros((0, X.shape[1], X.shape[2], 1), dtype=np.float32)
        empty_zones = np.array([], dtype=int)

        if cache_file:
            np.savez_compressed(
                cache_file, heatmaps_all=empty_heatmaps, zones_all=empty_zones
            )

        return empty_heatmaps, empty_zones

    heatmaps_all = np.stack(pooled_heatmaps, axis=0).astype(np.float32)
    zones_all = np.array(pooled_zones, dtype=int)

    if cache_file:
        np.savez_compressed(
            cache_file, heatmaps_all=heatmaps_all, zones_all=zones_all
        )
        print("Saved pooled heatmaps cache:", cache_file, "shape:", heatmaps_all.shape)

    return heatmaps_all, zones_all