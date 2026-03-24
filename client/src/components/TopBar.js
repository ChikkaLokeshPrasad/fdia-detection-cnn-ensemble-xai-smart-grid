import React, { useState, useEffect } from "react"

function TopBar({ pipelineStatus }) {

  const [time, setTime] = useState(new Date())

  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(t)
  }, [])

  const logout = () => {
    localStorage.removeItem("token")
    window.location.reload()
  }

  const statusColor = {
    idle:    "var(--text-secondary)",
    running: "var(--amber)",
    success: "var(--green)",
    error:   "var(--red)"
  }

  const statusLabel = {
    idle:    "STANDBY",
    running: "PIPELINE RUNNING",
    success: "PIPELINE COMPLETE",
    error:   "PIPELINE ERROR"
  }

  const status = pipelineStatus?.lastStatus || "idle"

  return (
    <div className="topbar">
      <div style={{ display: "flex", alignItems: "center" }}>
        <span className="topbar-logo">⚡ GRID MONITOR</span>
        <span className="topbar-sep" />
        <span className="topbar-subtitle">
          FDIA Detection System — IEEE 13-Bus Distribution Network
        </span>
      </div>

      <div className="topbar-right">
        <div style={{
          display: "flex", alignItems: "center", gap: 7,
          fontFamily: "var(--font-mono)", fontSize: 11,
          color: statusColor[status]
        }}>
          <span style={{
            width: 6, height: 6, borderRadius: "50%",
            background: statusColor[status],
            boxShadow: `0 0 6px ${statusColor[status]}`,
            animation: status === "running" ? "blink 0.8s ease infinite" : "none"
          }} />
          {statusLabel[status]}
        </div>

        <span className="topbar-sep" />

        <span className="topbar-time">
          {time.toLocaleTimeString("en-US", {
            hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false
          })}
        </span>

        <button className="btn" onClick={logout} style={{ padding: "6px 14px" }}>
          Logout
        </button>
      </div>
    </div>
  )
}

export default TopBar