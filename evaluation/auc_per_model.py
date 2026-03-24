import numpy as np
from sklearn.metrics import roc_auc_score
from tensorflow.keras.models import load_model

X_test = np.load("saved_models/X_test.npy")
y_test = np.load("saved_models/y_test.npy")

alphas = [0.5, 0.8, 1.0, 1.2, 1.5]

for a in alphas:
    model = load_model(f"saved_models/detector_alpha_{a}.keras")

    preds = model.predict(X_test).ravel()

    auc = roc_auc_score(y_test, preds)

    print(f"AUC of detector_alpha_{a}: {auc:.6f}")