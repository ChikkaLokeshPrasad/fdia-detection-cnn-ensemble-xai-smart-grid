SEED = 42

# Dataset paths
MAT_X   = "datasets/2D_Array_13_Bus_X.mat"
MAT_Y   = "datasets/2D_Array_13_Bus_Y.mat"
MAT_LOC = "datasets/2D_Array_13_Bus_Loc.mat"

DIR_MODELS  = "saved_models"
DIR_RESULTS = "results"

BALANCING_RATIOS = [0.5, 0.8, 1.0, 1.2, 1.5]

DATASET_CONFIG = {
    "use_real_dataset":      True,
    "n_buses":               23,    # 13 physical buses x phases = 23 measurement nodes
    "n_phases":              1,
    "time_window":           11,    # actual time steps in dataset
    "samples":               5000,
    "attack_fraction":       0.025,
    "attack_strength_range": (-0.05, 0.05),
}

MODEL_CONFIG = {
    # Three Conv2D layers matching paper: 32 -> 64 -> 128 filters
    "cnn_filters":  [32, 64, 128],
    "kernel_size":  (3, 3),
    "pool_size":    (2, 1),
    "dense_units":  64,
    "dropout":      0.3,
    "lr":           1e-3,
    "batch_size":   32,

    # Increased from 25 -> 50 epochs and patience 5 -> 10
    # Deeper 32-64-128 network needs more epochs to converge
    # This matches paper's implementation details
    "epochs":       50,
    "patience":     10,
}