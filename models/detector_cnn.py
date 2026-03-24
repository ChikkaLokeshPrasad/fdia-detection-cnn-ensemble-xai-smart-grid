from tensorflow.keras import layers, models, optimizers
from config.config import MODEL_CONFIG


def build_detection_cnn(input_shape, cfg=MODEL_CONFIG):
    """
    Spatiotemporal CNN detector matching paper architecture:
    Conv2D (32) → BN → ReLU → Pool
    Conv2D (64) → BN → ReLU → Pool
    Conv2D (128) → BN → ReLU
    GlobalAveragePooling → Dense → Dropout → Sigmoid
    """
    inp = layers.Input(shape=input_shape)
    x   = inp

    for f in cfg["cnn_filters"]:
        x = layers.Conv2D(
            f,
            cfg["kernel_size"],
            padding="same",
            use_bias=False          # BN handles bias
        )(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation("relu")(x)

        # Only pool if spatial dims allow it
        if x.shape[1] > 1 and x.shape[2] > 1:
            x = layers.MaxPooling2D(cfg["pool_size"])(x)

    # GlobalAveragePooling as described in the paper
    x   = layers.GlobalAveragePooling2D()(x)
    x   = layers.Dense(cfg["dense_units"], activation="relu")(x)
    x   = layers.Dropout(cfg["dropout"])(x)
    out = layers.Dense(1, activation="sigmoid")(x)

    model = models.Model(inputs=inp, outputs=out)

    model.compile(
        optimizer=optimizers.Adam(cfg["lr"]),
        loss="binary_crossentropy",
        metrics=["AUC"],
    )

    return model