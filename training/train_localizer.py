import numpy as np
from collections import Counter

from sklearn.model_selection import train_test_split

from tensorflow.keras import callbacks

from models.localizer_cnn import build_localizer_cnn

from config.config import MODEL_CONFIG, SEED


# ---------------------------
# Train pooled localizer
# ---------------------------
def train_pooled_localizer(heatmaps_all, zones_all, zones_def, cfg=MODEL_CONFIG):
    if heatmaps_all.shape[0] == 0:
        print("No pooled heatmaps to train localizer.")
        return None
    class_counts = Counter(zones_all)
    print("Pooled localizer class counts:", class_counts)
    valid_mask = zones_all >= 0
    X_hm = heatmaps_all[valid_mask]
    y_z = zones_all[valid_mask]
    N_examples = len(y_z)
    if N_examples < 2:
        print("Not enough pooled heatmaps:", N_examples)
        return None

    # stratified if possible
    min_count = min(class_counts.values())
    n_classes = len(class_counts)
    if min_count >= 2 and n_classes >= 2:
        Xtr, Xv, ytr, yv = train_test_split(
            X_hm, y_z, test_size=0.2, random_state=SEED, stratify=y_z
        )
    else:
        Xtr, Xv, ytr, yv = train_test_split(
            X_hm, y_z, test_size=0.2, random_state=SEED, shuffle=True
        )
        print("[Localizer] used non-stratified split due to class imbalance.")

    input_shape = Xtr.shape[1:]
    n_zones = len(zones_def)
    loc_model = build_localizer_cnn(input_shape, n_zones, cfg)
    es = callbacks.EarlyStopping(
        monitor="val_loss", patience=cfg["patience"], restore_best_weights=True
    )
    loc_model.fit(
        Xtr,
        ytr,
        validation_data=(Xv, yv),
        epochs=cfg["epochs"],
        batch_size=cfg["batch_size"],
        callbacks=[es],
        verbose=1,
    )
    return loc_model



# ---------------------------
# Localization voting (here just one pooled localizer)
# ---------------------------
def localize_ensemble(localizers, per_model_heatmap_for_sample, zones_def):
    """
    localizers: list of (label, model) pairs.
    per_model_heatmap_for_sample: list of (alpha, heatmap( H,W,1 )) for that sample.
    Here we use only the pooled localizer and just pick the first heatmap.
    """
    votes = []
    for label, model in localizers:
        if model is None:
            continue
        if len(per_model_heatmap_for_sample) == 0:
            continue
        hm = per_model_heatmap_for_sample[0][1]  # just first heatmap
        pred = model.predict(hm[np.newaxis, ...], verbose=0)
        zone = np.argmax(pred, axis=1)[0]
        votes.append(int(zone))
    if len(votes) == 0:
        return -1
    vals, counts = np.unique(votes, return_counts=True)
    maj_zone = vals[np.argmax(counts)]
    return int(maj_zone)
