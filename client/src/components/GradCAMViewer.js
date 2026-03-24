import React, { useState, useEffect } from "react"

const BASE = "http://localhost:5000/results/gradcam_examples"

const TABS = [
  { key: "TP",  label: "True Positives",      color: "var(--green)" },
  { key: "FP",  label: "False Positives",      color: "var(--amber)" },
  { key: "MIS", label: "Misclassifications",   color: "var(--red)"   },
]

function GradCAMViewer() {

  const [activeTab, setActiveTab] = useState("TP")
  const [files, setFiles]         = useState([])
  const [selected, setSelected]   = useState(0)

  // Fetch the list of gradcam example filenames from the server
  useEffect(() => {
    fetch("http://localhost:5000/api/gradcam-files")
      .then(r => r.json())
      .then(data => setFiles(data.files || []))
      .catch(() => {
        // Fallback: use known filename patterns if API not available
        setFiles([
          "TP_idx0_zone-1_y0.png",
          "TP_idx1_zone-1_y0.png",
          "TP_idx2_zone-1_y0.png",
          "FP_idx0_zone-1_y0.png",
          "FP_idx1_zone-1_y0.png",
          "MIS_idx0_zone-1_y0.png",
          "MIS_idx1_zone-1_y0.png",
        ])
      })
  }, [])

  const filtered = files.filter(f => f.startsWith(activeTab + "_"))

  const activeColor = TABS.find(t => t.key === activeTab)?.color || "var(--cyan)"

  return (
    <div className="panel">
      <div className="panel-label">Grad-CAM Heatmaps</div>

      {/* Tab strip */}
      <div className="tab-strip">
        {TABS.map(tab => (
          <button
            key={tab.key}
            className={`tab-btn ${activeTab === tab.key ? "active" : ""}`}
            style={activeTab === tab.key ? {
              color: tab.color,
              borderBottomColor: tab.color
            } : {}}
            onClick={() => { setActiveTab(tab.key); setSelected(0) }}
          >
            {tab.label}
            <span style={{
              marginLeft: 6,
              fontFamily: "var(--font-mono)",
              fontSize: 9,
              color: activeTab === tab.key ? tab.color : "var(--text-muted)"
            }}>
              ({files.filter(f => f.startsWith(tab.key + "_")).length})
            </span>
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div style={{
          padding: "40px 0", textAlign: "center",
          fontFamily: "var(--font-mono)", fontSize: 12,
          color: "var(--text-muted)"
        }}>
          NO HEATMAPS AVAILABLE — RUN PIPELINE FIRST
        </div>
      ) : (
        <>
          {/* Main selected image */}
          <div className="img-viewer" style={{ marginBottom: 12 }}>
            <img
              src={`${BASE}/${filtered[selected]}`}
              alt={filtered[selected]}
              style={{ maxHeight: 200 }}
            />
            <div className="img-viewer-label">
              {filtered[selected]}
            </div>
          </div>

          {/* Thumbnail strip */}
          <div style={{ display: "flex", gap: 8, overflowX: "auto", paddingBottom: 4 }}>
            {filtered.map((f, i) => (
              <div
                key={f}
                onClick={() => setSelected(i)}
                style={{
                  flexShrink: 0, width: 70, cursor: "pointer",
                  border: `1px solid ${i === selected ? activeColor : "var(--border)"}`,
                  borderRadius: "var(--radius)",
                  overflow: "hidden",
                  opacity: i === selected ? 1 : 0.5,
                  transition: "opacity 0.2s, border-color 0.2s",
                  boxShadow: i === selected ? `0 0 8px ${activeColor}44` : "none"
                }}
              >
                <img
                  src={`${BASE}/${f}`}
                  alt={f}
                  style={{ width: "100%", display: "block" }}
                />
              </div>
            ))}
          </div>

          {/* Info row */}
          <div style={{
            marginTop: 10,
            display: "flex", gap: 16,
            fontFamily: "var(--font-mono)", fontSize: 10,
            color: "var(--text-secondary)"
          }}>
            <span>Each column = one α detector (0.5 → 1.5)</span>
            <span style={{ marginLeft: "auto" }}>
              {selected + 1} / {filtered.length}
            </span>
          </div>
        </>
      )}
    </div>
  )
}

export default GradCAMViewer