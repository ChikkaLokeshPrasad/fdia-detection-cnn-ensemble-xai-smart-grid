import numpy as np
import os

from config.config import DIR_MODELS
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from tensorflow.keras import callbacks

from models.detector_cnn import build_detection_cnn
from models.meta_cnn import build_meta_cnn
from config.config import MODEL_CONFIG, BALANCING_RATIOS, SEED


def _smote_resample(X_flat, y, alpha, random_state=SEED):
    """
    Apply SMOTE with k=5 neighbors as described in the paper.
    alpha controls the desired ratio of normal:attack samples.
    X_flat: (N, H*W) flattened features for SMOTE
    Returns resampled X_flat, y
    """
    try:
        from imblearn.over_sampling import SMOTE
    except ImportError:
        raise ImportError(
            "imbalanced-learn is required. "
            "Install it with: pip install imbalanced-learn"
        )

    idx_attack = np.where(y == 1)[0]
    idx_normal = np.where(y == 0)[0]

    n_attack = len(idx_attack)
    n_normal = len(idx_normal)

    if n_attack == 0:
        return X_flat, y

    # Target number of normal samples based on alpha ratio
    desired_normal = int(alpha * n_attack)

    # SMOTE requires at least k+1 minority samples
    k_neighbors = min(5, n_attack - 1)

    if k_neighbors < 1:
        print(f"  [SMOTE] Not enough attack samples ({n_attack}), using random resampling.")
        return _fallback_resample(X_flat, y, alpha, random_state)

    # Subsample normal class to desired ratio before SMOTE
    if desired_normal <= n_normal:
        sel_normal = np.random.choice(idx_normal, desired_normal, replace=False)
    else:
        sel_normal = np.random.choice(idx_normal, desired_normal, replace=True)

    subset_idx = np.concatenate([sel_normal, idx_attack])
    X_sub      = X_flat[subset_idx]
    y_sub      = y[subset_idx]

    # Apply SMOTE to balance the subset
    smote = SMOTE(k_neighbors=k_neighbors, random_state=random_state)

    try:
        X_res, y_res = smote.fit_resample(X_sub, y_sub)
        print(f"  [SMOTE] alpha={alpha}: {len(y_sub)} -> {len(y_res)} samples "
              f"(attacks: {(y_res==1).sum()}, normal: {(y_res==0).sum()})")
        return X_res, y_res
    except Exception as e:
        print(f"  [SMOTE] Failed ({e}), falling back to random resampling.")
        return _fallback_resample(X_flat, y, alpha, random_state)


def _fallback_resample(X_flat, y, alpha, random_state=SEED):
    """
    Fallback random resampling if SMOTE fails.
    """
    idx_attack = np.where(y == 1)[0]
    idx_normal = np.where(y == 0)[0]
    n_attack   = len(idx_attack)
    n_normal   = len(idx_normal)

    desired_normal = int(alpha * n_attack)

    if desired_normal <= n_normal:
        sel_normal = np.random.choice(idx_normal, desired_normal, replace=False)
    else:
        sel_normal = np.random.choice(idx_normal, desired_normal, replace=True)

    subset_idx = np.concatenate([sel_normal, idx_attack])
    np.random.shuffle(subset_idx)

    return X_flat[subset_idx], y[subset_idx]


def train_detection_ensemble(X, y, balancing_ratios=BALANCING_RATIOS, cfg=MODEL_CONFIG):
    """
    Train 5 CNN detectors on SMOTE-resampled subsets with
    different class balancing ratios alpha in {0.5, 0.8, 1.0, 1.2, 1.5}.
    Outputs are fused using a learnable Conv1D meta-network.
    """

    # Train / val / test split (70:15:15) as stated in paper
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y,
        test_size=0.15,
        random_state=SEED,
        stratify=y
    )

    np.save(os.path.join(DIR_MODELS, "X_test.npy"), X_test)
    np.save(os.path.join(DIR_MODELS, "y_test.npy"), y_test)

    # Holdout from train_val for meta-CNN training (15% of total ~ 70:15:15)
    X_train, X_holdout, y_train, y_holdout = train_test_split(
        X_train_val,
        y_train_val,
        test_size=0.176,
        random_state=SEED,
        stratify=y_train_val,
    )

    print(f"Split -> Train: {len(y_train)}, Holdout: {len(y_holdout)}, Test: {len(y_test)}")
    print(f"Attacks -> Train: {y_train.sum()}, Holdout: {y_holdout.sum()}, Test: {y_test.sum()}")

    input_shape  = X.shape[1:]
    flat_dim     = int(np.prod(input_shape))
    X_train_flat = X_train.reshape(len(X_train), flat_dim)

    cnn_models = []
    hist_list  = []

    # Train one CNN per balancing ratio using SMOTE
    for alpha in balancing_ratios:

        print(f"\nTraining CNN for alpha={alpha}...")

        X_res_flat, y_res = _smote_resample(
            X_train_flat, y_train, alpha, random_state=SEED
        )

        # Reshape back to (N, H, W, C)
        X_res = X_res_flat.reshape(-1, *input_shape)

        # Shuffle
        perm  = np.random.permutation(len(y_res))
        X_res = X_res[perm]
        y_res = y_res[perm]

        model = build_detection_cnn(input_shape, cfg)

        es = callbacks.EarlyStopping(
            monitor="val_AUC",
            patience=cfg["patience"],
            restore_best_weights=True,
            mode="max"
        )

        # Reduce LR when val_loss plateaus - helps converge to tighter boundary
        reduce_lr = callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=3,
            min_lr=1e-6,
            verbose=0
        )

        history = model.fit(
            X_res, y_res,
            epochs=cfg["epochs"],
            batch_size=cfg["batch_size"],
            validation_data=(X_holdout, y_holdout),
            callbacks=[es, reduce_lr],
            verbose=0,
        )

        print(f"  Trained CNN alpha={alpha} on {len(y_res)} samples "
              f"(attacks: {(y_res==1).sum()}, normal: {(y_res==0).sum()})")

        model.save(os.path.join(DIR_MODELS, f"detector_alpha_{alpha}.keras"))

        cnn_models.append((alpha, model))
        hist_list.append(history)

    # Build meta-features on holdout
    meta_X = []
    for (alpha, model) in cnn_models:
        preds = model.predict(
            X_holdout, batch_size=cfg["batch_size"], verbose=0
        ).ravel()
        meta_X.append(preds)

    meta_X     = np.vstack(meta_X).T
    meta_X_cnn = meta_X[..., np.newaxis].astype("float32")

    # Train Conv1D meta-network
    meta_cnn = build_meta_cnn(meta_X_cnn.shape[1], lr=cfg["lr"])

    es_meta = callbacks.EarlyStopping(
        monitor="val_AUC",
        patience=cfg["patience"],
        restore_best_weights=True,
        mode="max"
    )

    reduce_lr_meta = callbacks.ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.5,
        patience=3,
        min_lr=1e-6,
        verbose=0
    )

    meta_cnn.fit(
        meta_X_cnn,
        y_holdout,
        validation_split=0.2,
        epochs=100,
        batch_size=32,
        callbacks=[es_meta, reduce_lr_meta],
        verbose=0,
    )

    print("\nTrained Conv1D meta-fusion network on holdout meta-features.")
    meta_cnn.save(os.path.join(DIR_MODELS, "meta_cnn.keras"))

    # Ensemble predict function
    def ensemble_predict_on_set(X_set):
        per_model_preds = []
        for (alpha, model) in cnn_models:
            per_model_preds.append(
                model.predict(
                    X_set, batch_size=cfg["batch_size"], verbose=0
                ).ravel()
            )
        M     = np.vstack(per_model_preds).T
        M_cnn = M[..., np.newaxis].astype("float32")
        probs = meta_cnn.predict(
            M_cnn, batch_size=cfg["batch_size"], verbose=0
        ).ravel()
        return probs

    probs_test = ensemble_predict_on_set(X_test)
    auc        = roc_auc_score(y_test, probs_test)

    print(f"\nEnsemble AUC on test set: {auc:.4f}")

    return {
        "cnn_models":          cnn_models,
        "meta_cnn":            meta_cnn,
        "X_test":              X_test,
        "y_test":              y_test,
        "ensemble_predict_fn": ensemble_predict_on_set,
        "X_holdout":           X_holdout,
        "y_holdout":           y_holdout,
        "auc_test":            auc,
    }