import React, { useState } from "react"

const BASE = "http://localhost:5000/results"

const GRAPHS = [
  {
    key: "roc",
    label: "ROC Curve",
    src: `${BASE}/roc_curve.png`,
    desc: "Receiver Operating Characteristic — True Positive Rate vs False Positive Rate. Near-vertical ascent indicates excellent class separation."
  },
  {
    key: "pr",
    label: "Precision-Recall",
    src: `${BASE}/pr_curve.png`,
    desc: "Precision-Recall tradeoff across detection thresholds. High area under curve indicates reliable detection under class imbalance conditions."
  },
  {
    key: "alpha",
    label: "α vs AUC",
    src: `${BASE}/alpha_vs_auc.png`,
    desc: "Detector AUC performance across five class balancing ratios (α = 0.5 to 1.5). Shows how resampling ratio affects each individual CNN's detection capability."
  },
  {
    key: "zone",
    label: "Zone Accuracy",
    src: `${BASE}/zone_accuracy.png`,
    desc: "Localization accuracy per distribution zone. Shows how precisely the system can identify which zone of the 13-bus network is under attack."
  },
  {
    key: "roc_pr",
    label: "Combined",
    src: `${BASE}/roc_pr.png`,
    desc: "ROC and Precision-Recall curves side by side for publication-ready comparison."
  },
]

function GraphPanel() {

  const [active, setActive] = useState("roc")

  const current = GRAPHS.find(g => g.key === active)

  return (
    <div className="panel">
      <div className="panel-label">Model Performance — Evaluation Graphs</div>

      <div className="tab-strip">
        {GRAPHS.map(g => (
          <button
            key={g.key}
            className={`tab-btn ${active === g.key ? "active" : ""}`}
            onClick={() => setActive(g.key)}
          >
            {g.label}
          </button>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 280px", gap: 16 }}>

        {/* Graph image */}
        <div className="img-viewer">
          <img
            key={current.src}
            src={current.src}
            alt={current.label}
            style={{ maxHeight: 340, objectFit: "contain" }}
            onError={e => {
              e.target.style.display = "none"
            }}
          />
          <div className="img-viewer-label">{current.src.split("/").pop()}</div>
        </div>

        {/* Description + metrics reference */}
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <div style={{
            padding: "12px 14px",
            background: "var(--bg-panel-alt)",
            border: "1px solid var(--border)",
            borderRadius: "var(--radius)"
          }}>
            <div style={{
              fontFamily: "var(--font-label)", fontSize: 10,
              letterSpacing: 2, textTransform: "uppercase",
              color: "var(--cyan)", marginBottom: 8
            }}>
              {current.label}
            </div>
            <p style={{
              fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.7
            }}>
              {current.desc}
            </p>
          </div>

          {/* Paper benchmarks */}
          <div style={{
            padding: "12px 14px",
            background: "var(--bg-panel-alt)",
            border: "1px solid var(--border)",
            borderRadius: "var(--radius)"
          }}>
            <div style={{
              fontFamily: "var(--font-label)", fontSize: 10,
              letterSpacing: 2, textTransform: "uppercase",
              color: "var(--amber)", marginBottom: 10
            }}>
              Paper Benchmarks
            </div>
            {[
              ["AUC",             "0.9994"],
              ["Detection Rate",  "99.83%"],
              ["Hamming Loss",    "0.50%"],
              ["Localization",    "99.50%"],
              ["Latency",         "27 ms"],
            ].map(([label, val]) => (
              <div key={label} style={{
                display: "flex", justifyContent: "space-between",
                marginBottom: 6,
                fontFamily: "var(--font-mono)", fontSize: 11
              }}>
                <span style={{ color: "var(--text-secondary)" }}>{label}</span>
                <span style={{ color: "var(--cyan)" }}>{val}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default GraphPanel