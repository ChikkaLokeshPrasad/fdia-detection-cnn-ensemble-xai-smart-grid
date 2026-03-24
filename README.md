# False Data Injection Attack Detection and Localization Framework

**False Data Injection Attack Detection Using CNN Ensembles with Localization and Explainable AI Integration in Smart Power Distribution Systems**

> Final Major Project — Department of AI & ML  
> CMR College of Engineering & Technology, Medchal, Telangana  

---

## Overview

A real-time cyber-security monitoring system for IEEE 13-bus smart power distribution networks. The system detects False Data Injection Attacks (FDIA) in DSSE voltage measurements using a spatiotemporal CNN ensemble, localizes the attacked bus zone, and provides explainable AI insights via GradCAM and SHAP.

---

## Results

| Metric | Our Result | Paper Target |
|---|---|---|
| Ensemble AUC | 0.9991 | 0.9994 |
| Recall (Detection Rate) | 97.85% | 99.83% |
| F1 Score | 0.9286 | ~0.94 |
| Localization Accuracy | 99.50% | 99.50% |
| Inference Latency | 27 ms/window | 27 ms |

---

## Architecture

```
DSSE Voltage Measurements (IEEE 13-Bus)
            ↓
    Data Preprocessing
    (SMOTE resampling × 5, Normalization)
            ↓
  CNN Ensemble (F1–F5)          ← 5 detectors, α ∈ {0.5, 0.8, 1.0, 1.2, 1.5}
  Conv2D(32) → Conv2D(64) → Conv2D(128) → GlobalAvgPool → Sigmoid
            ↓
  Conv1D Meta-Fusion Network    ← learnable end-to-end fusion
            ↓
  ┌─────────────┬──────────────┬─────────────┐
  Detection     Localization   Explainability
  (τ = 0.55)   (Zone 0–6)     (SHAP + GradCAM)
```

---

## Project Structure

```
Final Major Project/
├── client/                  React dashboard
│   └── src/
│       ├── components/      AttackStatus, GridVisualization,
│       │                    GradCAMViewer, ShapViewer,
│       │                    GraphPanel, TopBar
│       └── pages/           Dashboard, Login
├── server/                  Node.js + Express API
│   ├── routes/              authRoutes, pipelineRoutes
│   ├── middleware/          auth (JWT)
│   └── server.js
├── config/
│   └── config.py            Global configuration
├── data/
│   ├── data_loader.py       MATLAB dataset loader
│   └── preprocessing.py     Spatiotemporal normalization
├── models/
│   ├── detector_cnn.py      CNN detector (32-64-128)
│   ├── meta_cnn.py          Conv1D fusion network
│   └── localizer_cnn.py     GradCAM-based localizer
├── training/
│   ├── train_detectors.py   SMOTE + ensemble training
│   ├── train_localizer.py   Pooled heatmap localizer
│   └── train_meta.py        Meta CNN training
├── evaluation/
│   ├── metrics.py           AUC per detector
│   ├── plots.py             ROC, PR, alpha vs AUC, zone accuracy
│   ├── localization_metrics.py  Per-zone confusion
│   └── experiment_report.py    Full metrics report
├── explainability/
│   ├── gradcam.py           GradCAM heatmap generation
│   └── shap_explainer.py    SHAP feature attribution
├── datasets/                MATLAB dataset files (not tracked)
├── saved_models/            Trained .keras models (not tracked)
├── results/                 Generated graphs and JSON
└── main.py                  Pipeline entry point
```

---

## Setup

### Prerequisites

```
Python 3.10+
Node.js 18+
TensorFlow 2.10
```

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

### 2. Python environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
pip install imbalanced-learn
```

### 3. Datasets

The MATLAB dataset files are included in the repository under `datasets/`:
```
datasets/2D_Array_13_Bus_X.mat    (31MB - IEEE 13-bus voltage measurements)
datasets/2D_Array_13_Bus_Y.mat    (attack labels)
datasets/2D_Array_13_Bus_Loc.mat  (attacked bus locations)
```
No additional setup needed - datasets are ready to use after cloning.

### 4. Server setup

```bash
cd server
npm install
```

Create `server/.env`:
```
PORT=5000
JWT_SECRET=your_secret_here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_password_here
PYTHON_PATH=path/to/venv/Scripts/python.exe
PROJECT_ROOT=path/to/project/root
```

### 5. React setup

```bash
cd client
npm install
```

---

## Running the Project

**Terminal 1 — Node server:**
```bash
cd server
node server.js
```

**Terminal 2 — React frontend:**
```bash
cd client
npm start
```

**Run the ML pipeline** from the dashboard UI by clicking **RUN FDIA DETECTION**, or directly:
```bash
python main.py
```

---

## Dataset

- **Source:** IEEE 13-bus distribution system DSSE voltage measurements
- **Format:** MATLAB `.mat` files
- **Shape:** X → `(25910, 23, 11)`, Y → `(25910, 1)`, Loc → `(25910, 1)`
- **Samples:** 25,910 total — 618 attacks (2.4%), 25,292 normal
- **Buses:** 23 measurement nodes across 13 physical buses
- **Time steps:** 11 per window

---

## Technology Stack

| Layer | Technology |
|---|---|
| ML Framework | TensorFlow 2.10 / Keras |
| Resampling | imbalanced-learn (SMOTE) |
| Explainability | SHAP, GradCAM |
| Backend | Node.js, Express, JWT |
| Frontend | React, CSS Variables |
| Data | NumPy, SciPy, Matplotlib |

---

## Key Design Decisions

- **SMOTE resampling** with k=5 neighbors across 5 balancing ratios (α = 0.5–1.5) to handle extreme class imbalance (2.4% attack rate)
- **Conv1D meta-fusion** instead of fixed SVM — enables end-to-end gradient optimization
- **GradCAM pseudo-labels** for localization training — no manual bus-level annotation required
- **Detection threshold τ = 0.55** — raised from 0.5 to reduce false positives
- **GlobalAveragePooling** in detector CNNs as described in the paper

---

## Authors

- Mrs. Sakina H. Sayyed — Assistant Professor, Dept. of AI & ML
- CH. Lokesh Prasad — Student (Chikkalokeshprasad04@gmail.com)
- K. Harsha Vardhan Reddy — Student (harshavardhanreddykota21@gmail.com)

---

## Reference

> False Data Injection Attack Detection Using CNN Ensembles with Localization and Explainable AI Integration in Smart Power Distribution Systems  
> CMR College of Engineering & Technology, 2026