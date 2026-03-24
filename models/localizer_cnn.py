from tensorflow.keras import layers, models, optimizers
from config.config import MODEL_CONFIG


def build_localizer_cnn(input_shape, n_zones, cfg=MODEL_CONFIG):
    inp = layers.Input(shape=input_shape)
    x = layers.Conv2D(8, (3, 3), activation="relu", padding="same")(inp)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Conv2D(16, (3, 3), activation="relu", padding="same")(x)
    x = layers.Flatten()(x)
    x = layers.Dense(64, activation="relu")(x)
    out = layers.Dense(n_zones, activation="softmax")(x)
    model = models.Model(inputs=inp, outputs=out)
    model.compile(
        optimizer=optimizers.Adam(cfg["lr"]),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model
