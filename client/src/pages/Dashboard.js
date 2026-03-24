import React, { useState, useEffect, useCallback } from "react"

import TopBar            from "../components/TopBar"
import AttackStatus      from "../components/AttackStatus"
import GridVisualization from "../components/GridVisualization"
import GradCAMViewer     from "../components/GradCAMViewer"
import ShapViewer        from "../components/ShapViewer"
import GraphPanel        from "../components/GraphPanel"

import api from "../api"

function Dashboard() {

  const [dashData,        setDashData]        = useState(null)
  const [pipelineStatus,  setPipelineStatus]  = useState({ lastStatus: "idle" })
  const [running,         setRunning]         = useState(false)

  const token = localStorage.getItem("token")

  // ── Single data fetch, passed as props — no redundant calls ──────────────
  const fetchDashboard = useCallback(async () => {
    try {
      const res = await api.get("/dashboard-data")
      setDashData(res.data)
    } catch (err) {
      console.error("Dashboard data fetch failed:", err)
    }
  }, [])

  const fetchPipelineStatus = useCallback(async () => {
    try {
      const res = await api.get("/pipeline/status", {
        headers: { Authorization: token }
      })
      setPipelineStatus(res.data)
    } catch (_) {}
  }, [token])

  // Poll dashboard data every 5s and pipeline status every 2s
  useEffect(() => {
    fetchDashboard()
    fetchPipelineStatus()

    const dashInterval     = setInterval(fetchDashboard,        5000)
    const statusInterval   = setInterval(fetchPipelineStatus,   2000)

    return () => {
      clearInterval(dashInterval)
      clearInterval(statusInterval)
    }
  }, [fetchDashboard, fetchPipelineStatus])

  // Detect when pipeline transitions to success → refresh dashboard
  useEffect(() => {
    if (pipelineStatus.lastStatus === "success") {
      setRunning(false)
      setTimeout(fetchDashboard, 1000)
    }
    if (pipelineStatus.lastStatus === "error") {
      setRunning(false)
    }
  }, [pipelineStatus.lastStatus, fetchDashboard])

  // ── Run pipeline ──────────────────────────────────────────────────────────
  const runPipeline = async () => {
    setRunning(true)
    try {
      await api.get("/pipeline/run", {
        headers: { Authorization: token }
      })
    } catch (err) {
      if (err.response?.status === 401) {
        alert("Session expired. Please login again.")
        localStorage.removeItem("token")
        window.location.reload()
      } else if (err.response?.status === 409) {
        alert("Pipeline is already running.")
      } else {
        alert("Failed to start pipeline. Is the server running?")
        setRunning(false)
      }
    }
  }

  const isAttack = (dashData?.attack_probability || 0) >= 0.5

  return (
    <div style={{ minHeight: "100vh" }}>

      <TopBar pipelineStatus={pipelineStatus} />

      <div className="dashboard">

        {/* ── Row 0: Run Controls ───────────────────────────────────────── */}
        <div style={{
          display: "flex", alignItems: "center",
          justifyContent: "space-between",
          padding: "10px 18px",
          background: "var(--bg-panel)",
          border: "1px solid var(--border)",
          borderRadius: "var(--radius)"
        }}>
          <div>
            <div style={{
              fontFamily: "var(--font-label)", fontSize: 10,
              letterSpacing: 3, textTransform: "uppercase",
              color: "var(--text-secondary)", marginBottom: 2
            }}>
              Pipeline Control
            </div>
            <div style={{
              fontFamily: "var(--font-mono)", fontSize: 11,
              color: "var(--text-muted)"
            }}>
              {pipelineStatus.lastRun
                ? `Last run: ${new Date(pipelineStatus.lastRun).toLocaleString()}`
                : "No pipeline run recorded"}
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            {running && (
              <div style={{
                display: "flex", alignItems: "center", gap: 8,
                fontFamily: "var(--font-mono)", fontSize: 11,
                color: "var(--amber)"
              }}>
                <span className="spinner" style={{
                  borderTopColor: "var(--amber)",
                  borderColor: "rgba(255,179,0,0.2)"
                }} />
                {pipelineStatus.lastMessage || "Starting pipeline..."}
              </div>
            )}

            <button
              className={`btn ${running ? "" : "amber"}`}
              onClick={runPipeline}
              disabled={running || pipelineStatus.lastStatus === "running"}
            >
              {running ? "RUNNING..." : "▶ RUN FDIA DETECTION"}
            </button>
          </div>
        </div>

        {/* ── Row 1: Attack alert banner (only when attack detected) ──────── */}
        {isAttack && dashData && (
          <div style={{
            padding: "12px 18px",
            background: "rgba(255,61,61,0.08)",
            border: "1px solid rgba(255,61,61,0.35)",
            borderRadius: "var(--radius)",
            display: "flex", alignItems: "center", gap: 14,
            animation: "fadeIn 0.3s ease"
          }}>
            <span style={{
              width: 8, height: 8, borderRadius: "50%",
              background: "var(--red)", boxShadow: "0 0 8px var(--red)",
              animation: "blink 0.8s ease infinite", flexShrink: 0
            }} />
            <div>
              <span style={{
                fontFamily: "var(--font-label)", fontSize: 11,
                letterSpacing: 2, textTransform: "uppercase",
                color: "var(--red)", marginRight: 12
              }}>
                ⚠ FDIA ATTACK DETECTED
              </span>
              <span style={{
                fontFamily: "var(--font-mono)", fontSize: 11,
                color: "var(--text-secondary)"
              }}>
                Probability: {(dashData.attack_probability * 100).toFixed(1)}%
                {dashData.predicted_zone >= 0 && ` · Zone ${dashData.predicted_zone} compromised`}
                {" "}· Ensemble AUC: {(dashData.ensemble_auc || 0).toFixed(4)}
              </span>
            </div>
          </div>
        )}

        {/* ── Row 2: Detection Status + Grid Topology ─────────────────────── */}
        <div className="row cols-2">
          <AttackStatus data={dashData} />
          <GridVisualization data={dashData} />
        </div>

        {/* ── Row 3: GradCAM + SHAP ────────────────────────────────────────── */}
        <div className="row cols-2">
          <GradCAMViewer />
          <ShapViewer />
        </div>

        {/* ── Row 4: Graphs (full width) ───────────────────────────────────── */}
        <GraphPanel />

        {/* ── Footer ───────────────────────────────────────────────────────── */}
        <div style={{
          padding: "12px 0",
          borderTop: "1px solid var(--border)",
          display: "flex", justifyContent: "space-between",
          fontFamily: "var(--font-mono)", fontSize: 10,
          color: "var(--text-muted)"
        }}>
          <span>CMR College of Engineering &amp; Technology · Dept. of AI &amp; ML</span>
          <span>False Data Injection Attack Detection · IEEE 13-Bus · CNN Ensemble + XAI</span>
        </div>

      </div>
    </div>
  )
}

export default Dashboard