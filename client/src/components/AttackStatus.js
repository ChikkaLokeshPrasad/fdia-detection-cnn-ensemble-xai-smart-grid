import React from "react"

function MetricRow({ label, value, color = "var(--text-primary)", bar = false, barPct = 0, barColor = "cyan" }) {
  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 4 }}>
        <span style={{
          fontFamily: "var(--font-label)", fontSize: 10,
          letterSpacing: 2, textTransform: "uppercase",
          color: "var(--text-secondary)"
        }}>
          {label}
        </span>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 14, color }}>
          {value}
        </span>
      </div>
      {bar && (
        <div className="progress-bar">
          <div className={`progress-fill ${barColor}`} style={{ width: `${barPct}%` }} />
        </div>
      )}
    </div>
  )
}

function AttackStatus({ data }) {

  if (!data) {
    return (
      <div className="panel" style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: 180 }}>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--text-muted)" }}>
          AWAITING MODEL OUTPUT...
        </span>
      </div>
    )
  }

  const prob = data.attack_probability || 0
  const isAttack = prob >= 0.5
  const zone = data.predicted_zone ?? -1

  return (
    <div className={`panel ${isAttack ? "red" : "green"}`}>
      <div className={`panel-label ${isAttack ? "red" : "green"}`}>
        Detection Status
      </div>

      {/* Main status + probability */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 20 }}>
        <div>
          <div className={`metric-value large ${isAttack ? "red" : "green"}`}>
            {(prob * 100).toFixed(1)}%
          </div>
          <div className="metric-label">Attack Probability</div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div className={`status-badge ${isAttack ? "attack" : "nominal"}`}>
            <span className="dot" />
            {isAttack ? "ATTACK DETECTED" : "NOMINAL"}
          </div>
          <div style={{
            marginTop: 10,
            fontFamily: "var(--font-mono)", fontSize: 12,
            color: isAttack ? "var(--red)" : "var(--text-secondary)"
          }}>
            Zone: {zone >= 0 ? `Z${zone}` : "—"}
          </div>
        </div>
      </div>

      <div className="progress-bar" style={{ marginBottom: 20 }}>
        <div
          className={`progress-fill ${isAttack ? "red" : ""}`}
          style={{ width: `${prob * 100}%` }}
        />
      </div>

      <div className="divider" />

      <MetricRow
        label="Ensemble AUC"
        value={(data.ensemble_auc || 0).toFixed(4)}
        color="var(--cyan)"
        bar barPct={(data.ensemble_auc || 0) * 100} barColor="cyan"
      />
      <MetricRow
        label="Precision"
        value={(data.precision || 0).toFixed(4)}
        bar barPct={(data.precision || 0) * 100}
      />
      <MetricRow
        label="Recall"
        value={(data.recall || 0).toFixed(4)}
        bar barPct={(data.recall || 0) * 100}
      />
      <MetricRow
        label="F1 Score"
        value={(data.f1_score || 0).toFixed(4)}
        color="var(--amber)"
        bar barPct={(data.f1_score || 0) * 100} barColor="amber"
      />

      <div className="divider" />

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <div>
          <div style={{ fontFamily: "var(--font-mono)", fontSize: 18, color: "var(--cyan)" }}>
            {data.total_attacks_detected ?? "—"}
          </div>
          <div className="metric-label">Attacks Detected</div>
        </div>
        <div>
          <div style={{ fontFamily: "var(--font-mono)", fontSize: 18, color: "var(--text-primary)" }}>
            {data.total_samples ?? "—"}
          </div>
          <div className="metric-label">Total Samples</div>
        </div>
      </div>
    </div>
  )
}

export default AttackStatus