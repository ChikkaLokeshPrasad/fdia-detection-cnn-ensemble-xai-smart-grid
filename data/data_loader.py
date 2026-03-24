import numpy as np
import scipy.io as sio
from config.config import MAT_X, MAT_Y, MAT_LOC



def define_zones(n_buses):
    """
    Simple zone definition: split buses into ~3-bus zones.
    You can replace this with the exact zones from the paper if needed.
    """
    n_zones = max(2, n_buses // 3)
    sizes = [n_buses // n_zones] * n_zones
    for i in range(n_buses % n_zones):
        sizes[i] += 1
    zones = []
    idx = 0
    for s in sizes:
        zones.append(list(range(idx, idx + s)))
        idx += s
    return zones


def load_mat_dataset(x_path=MAT_X, y_path=MAT_Y, loc_path=MAT_LOC):
    mat_x = sio.loadmat(x_path)
    mat_y = sio.loadmat(y_path)
    mat_loc = sio.loadmat(loc_path)

    def pick(mat, prefer):
        if prefer in mat:
            return prefer, mat[prefer]
        for k, v in mat.items():
            if not k.startswith("__"):
                return k, v
        return None, None

    kx, Xcand = pick(mat_x, "final")
    ky, Ycand = pick(mat_y, "Y")
    kl, Loccand = pick(mat_loc, "Loc")

    print("Using variables:", kx, ky, kl)

    X_raw = np.array(Xcand, dtype=np.float32)  # (N, H, T)
    y_raw = np.squeeze(np.array(Ycand))
    loc_raw = np.squeeze(np.array(Loccand))

    if y_raw.ndim > 1:
        y_raw = y_raw.squeeze()
    unique_y = np.unique(y_raw)
    print("Unique Y (raw):", unique_y)
    if set(unique_y).issubset({0, 1}):
        y = y_raw.astype(int)
    else:
        y = (y_raw != 0).astype(int)

    # location: 1-based bus indices in MATLAB -> convert to 0-based
    loc_proc = loc_raw.copy()
    if np.issubdtype(loc_proc.dtype, np.floating):
        loc_proc = np.where(np.isnan(loc_proc), -1, loc_proc)
    loc_proc = np.where(loc_proc == 0, -1, loc_proc)
    loc_nonneg = loc_proc[loc_proc >= 0]
    if loc_nonneg.size > 0 and loc_nonneg.max() > X_raw.shape[1] - 1:
        loc_proc = np.where(loc_proc >= 0, loc_proc - 1, -1)
        print("Detected loc indices likely 1-based, converting to 0-based.")
    loc_proc = loc_proc.astype(int)

    n_buses = X_raw.shape[1]
    zones_def = define_zones(n_buses)

    def map_bus_to_zone(bus_idx, zones):
        if bus_idx < 0:
            return -1
        for zid, z in enumerate(zones):
            if int(bus_idx) in z:
                return zid
        return -1

    attack_zone = np.array(
        [map_bus_to_zone(b, zones_def) for b in loc_proc], dtype=int
    )

    print(
        f"Loaded: N= {X_raw.shape[0]} H= {X_raw.shape[1]} T= {X_raw.shape[2]}"
    )
    print("Attacks:", int(y.sum()), "zones:", len(zones_def))
    return X_raw, y, attack_zone, zones_def



# ---------------------------
# Synthetic generator (optional)
# ---------------------------
def generate_synthetic_dsse(
    n_buses,
    n_phases,
    time_window,
    samples,
    attack_fraction,
    attack_strength_range,
):
    height = n_buses * n_phases
    X = np.zeros((samples, height, time_window), dtype=np.float32)
    y = np.zeros((samples,), dtype=np.int32)
    attack_zone = -np.ones((samples,), dtype=np.int32)
    t = np.arange(time_window)
    for i in range(samples):
        base = 1.0 + 0.01 * np.sin(2 * np.pi * (t + np.random.rand()) / time_window)
        for b in range(n_buses):
            noise = 0.005 * np.random.randn(time_window)
            X[i, b, :] = base + 0.002 * (b % 3) + noise
    n_attacked = max(1, int(samples * attack_fraction))
    attacked_idx = np.random.choice(samples, n_attacked, replace=False)
    for idx in attacked_idx:
        y[idx] = 1
        nb_target = np.random.choice([1, 2])
        targets = np.random.choice(n_buses, nb_target, replace=False)
        attack_zone[idx] = targets[0]
        if np.random.rand() < 0.5:
            start = np.random.randint(0, time_window // 2)
            c = np.random.uniform(*attack_strength_range)
            for b in targets:
                X[idx, b, start:] += c
        else:
            start = np.random.randint(0, time_window - 2)
            end = time_window
            c = np.linspace(
                0, np.random.uniform(*attack_strength_range), end - start
            )
            for b in targets:
                X[idx, b, start:end] += c
    return X, y, attack_zone
