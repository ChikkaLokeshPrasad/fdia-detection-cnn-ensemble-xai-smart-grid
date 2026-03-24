from tensorflow.keras import layers, models, optimizers


def build_meta_cnn(n_models, lr=1e-3):
    """
    Conv1D meta-classifier operating on K detector probabilities.
    Input shape: (K, 1)

    Kept simple intentionally - holdout set has only ~92 attack samples,
    a deeper network would overfit. Conv1D + single dense layer is optimal.
    """
    inp = layers.Input(shape=(n_models, 1))
    x   = layers.Conv1D(16, 2, activation="relu", padding="same")(inp)
    x   = layers.Flatten()(x)
    x   = layers.Dense(32, activation="relu")(x)
    x   = layers.Dropout(0.3)(x)
    out = layers.Dense(1, activation="sigmoid")(x)

    model = models.Model(inputs=inp, outputs=out)

    model.compile(
        optimizer=optimizers.Adam(lr),
        loss="binary_crossentropy",
        metrics=["AUC"],
    )

    return model