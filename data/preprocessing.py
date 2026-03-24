import numpy as np


# ---------------------------
# Preprocessing
# ---------------------------
def build_spatiotemporal_windows(X_raw):
    """Convert (N,H,T) -> (N,H,T,1) and normalize per-sample."""
    X = X_raw[..., np.newaxis].astype(np.float32)
    for i in range(X.shape[0]):
        s = X[i, ..., 0]
        mean = s.mean()
        std = s.std() if s.std() > 1e-6 else 1.0
        X[i, ..., 0] = (s - mean) / std
    return X
