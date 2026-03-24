import React, { useState } from "react"
import api from "../api"

function Login() {

  const [user,    setUser]    = useState("")
  const [pass,    setPass]    = useState("")
  const [error,   setError]   = useState("")
  const [loading, setLoading] = useState(false)

  const login = async () => {
    if (!user || !pass) { setError("USERNAME AND PASSWORD REQUIRED"); return }
    setLoading(true)
    setError("")
    try {
      const res = await api.post("/auth/login", { username: user, password: pass })
      localStorage.setItem("token", res.data.token)
      window.location.reload()
    } catch (err) {
      setError(err.response?.status === 401 ? "INVALID CREDENTIALS" : "SERVER UNREACHABLE")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-box">
        <div className="login-eyebrow">⚡ CMR College of Engineering &amp; Technology</div>
        <div className="login-heading">Grid Security Monitor</div>

        <div style={{
          marginBottom: 24, padding: "10px 14px",
          background: "rgba(0,200,255,0.05)",
          border: "1px solid var(--border)",
          borderRadius: "var(--radius)"
        }}>
          <div style={{ fontFamily: "var(--font-label)", fontSize: 10, letterSpacing: 2, textTransform: "uppercase", color: "var(--text-secondary)", marginBottom: 4 }}>System</div>
          <div style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-primary)" }}>
            FDIA Detection — IEEE 13-Bus Distribution Network
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Username</label>
          <input className="form-input" type="text" placeholder="admin"
            value={user} onChange={e => setUser(e.target.value)}
            onKeyDown={e => e.key === "Enter" && login()} />
        </div>

        <div className="form-group">
          <label className="form-label">Password</label>
          <input className="form-input" type="password" placeholder="••••••••"
            value={pass} onChange={e => setPass(e.target.value)}
            onKeyDown={e => e.key === "Enter" && login()} />
        </div>

        {error && <div className="form-error">{error}</div>}

        <button className="btn" onClick={login} disabled={loading}
          style={{ width: "100%", justifyContent: "center", marginTop: 20 }}>
          {loading ? <><span className="spinner" />&nbsp;AUTHENTICATING...</> : "AUTHENTICATE"}
        </button>

        <div style={{ marginTop: 20, fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--text-muted)", textAlign: "center" }}>
          Dept. of AI &amp; ML · Final Major Project
        </div>
      </div>
    </div>
  )
}

export default Login