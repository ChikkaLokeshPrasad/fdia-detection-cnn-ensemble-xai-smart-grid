import numpy as np
from sklearn.metrics import roc_auc_score
from tensorflow.keras.models import load_model

from config.config import DIR_MODELS


def compute_auc_per_detector():

    X_test = np.load(f"{DIR_MODELS}/X_test.npy")
    y_test = np.load(f"{DIR_MODELS}/y_test.npy")

    alphas = [0.5, 0.8, 1.0, 1.2, 1.5]

    auc_values = []

    for a in alphas:

        model = load_model(f"{DIR_MODELS}/detector_alpha_{a}.keras")

        preds = model.predict(X_test).ravel()

        auc = roc_auc_score(y_test, preds)

        print(f"AUC of detector_alpha_{a}: {auc:.6f}")

        auc_values.append(auc)

    return auc_values