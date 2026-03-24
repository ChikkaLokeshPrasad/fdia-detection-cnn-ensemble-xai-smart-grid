import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

from tensorflow.keras.models import load_model
from sklearn.metrics import roc_curve, precision_recall_curve

from config.config import DIR_RESULTS, DIR_MODELS


def plot_alpha_vs_auc(auc_values):

    alphas = [0.5, 0.8, 1.0, 1.2, 1.5]

    plt.figure(figsize=(6, 4))

    plt.plot(alphas, auc_values, marker='o')

    plt.xlabel("Balancing Ratio (α)")
    plt.ylabel("AUC")

    plt.title("Detector Performance vs Class Balancing Ratio")

    plt.grid(True)

    plt.tight_layout()

    plt.savefig(os.path.join(DIR_RESULTS, "alpha_vs_auc.png"), dpi=600)

    plt.close()

    print("Saved alpha_vs_auc graph")


def plot_zone_accuracy():

    csv_path = os.path.join(DIR_RESULTS, "per_zone_confusion.csv")

    if not os.path.exists(csv_path):
        print("Zone confusion file not found. Skipping zone accuracy plot.")
        return

    df = pd.read_csv(csv_path)

    acc = df["correct_localizations"] / df["detected"]

    plt.figure(figsize=(6, 4))

    plt.bar(df["zone"], acc)

    plt.xlabel("Zone")
    plt.ylabel("Localization Accuracy")

    plt.title("Localization Accuracy per Zone")

    plt.tight_layout()

    plt.savefig(os.path.join(DIR_RESULTS, "zone_accuracy.png"), dpi=600)

    plt.close()

    print("Saved zone_accuracy graph")


def plot_roc_pr():

    X_test = np.load(os.path.join(DIR_MODELS, "X_test.npy"))
    y_test = np.load(os.path.join(DIR_MODELS, "y_test.npy"))

    model = load_model(os.path.join(DIR_MODELS, "detector_alpha_1.0.keras"))

    preds = model.predict(X_test).ravel()

    fpr, tpr, _ = roc_curve(y_test, preds)
    prec, rec, _ = precision_recall_curve(y_test, preds)

    # ROC Curve
    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr)
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(DIR_RESULTS, "roc_curve.png"), dpi=600)
    plt.close()

    # Precision-Recall Curve
    plt.figure(figsize=(6, 5))
    plt.plot(rec, prec)
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(DIR_RESULTS, "pr_curve.png"), dpi=600)
    plt.close()

    # Combined ROC + PR
    plt.figure(figsize=(10, 4))

    plt.subplot(1, 2, 1)
    plt.plot(fpr, tpr)
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.plot(rec, prec)
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve")
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(os.path.join(DIR_RESULTS, "roc_pr.png"), dpi=600)
    plt.close()

    print("Saved ROC and PR curves")