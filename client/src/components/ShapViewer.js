import React from "react"

const BASE = "http://localhost:5000/results/shap"

function ShapViewer() {
  return (
    <div className="panel">
      <div className="panel-label amber">SHAP — Bus Feature Importance</div>

      <div style={{
        fontFamily: "var(--font-label)", fontSize: 10,
        letterSpacing: 2, textTransform: "uppercase",
        color: "var(--text-secondary)", marginBottom: 12
      }}>
        Detector α = 1.0 · Gradient Explainer · Mean |SHAP| per Bus
      </div>

      <div className="img-viewer">
        <img
          src={`${BASE}/detector_alpha_1.0_bus_importance.png`}
          alt="SHAP bus importance"
          onError={e => {
            e.target.style.display = "none"
            e.target.nextSibling.style.display = "flex"
          }}
        />
        <div style={{
          display: "none", padding: "40px 0",
          alignItems: "center", justifyContent: "center",
          fontFamily: "var(--font-mono)", fontSize: 12,
          color: "var(--text-muted)"
        }}>
          SHAP OUTPUT NOT FOUND — RUN PIPELINE FIRST
        </div>
        <div className="img-viewer-label">
          detector_alpha_1.0_bus_importance.png
        </div>
      </div>

      <div style={{
        marginTop: 14,
        padding: "10px 14px",
        background: "var(--bg-panel-alt)",
        border: "1px solid var(--border)",
        borderRadius: "var(--radius)"
      }}>
        <div style={{
          fontFamily: "var(--font-label)", fontSize: 10,
          letterSpacing: 2, color: "var(--amber)",
          textTransform: "uppercase", marginBottom: 8
        }}>
          How to read this chart
        </div>
        <p style={{
          fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.7
        }}>
          Each bar shows the mean absolute SHAP value for a bus index.
          Higher values indicate that bus contributed more to the model's
          attack detection decision. Buses with the highest importance
          are the most critical monitoring points in the distribution network.
        </p>
      </div>
    </div>
  )
}

export default ShapViewer