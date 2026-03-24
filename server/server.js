require("dotenv").config()

const express = require("express")
const cors    = require("cors")
const fs      = require("fs")
const path    = require("path")

const authRoutes     = require("./routes/authRoutes")
const pipelineRoutes = require("./routes/pipelineRoutes")

const app = express()

app.use(cors())
app.use(express.json())

app.use("/api/auth",     authRoutes)
app.use("/api/pipeline", pipelineRoutes)

// Serve result images and files statically
app.use("/results", express.static(path.join(__dirname, "../results")))

// ── Dashboard Data ────────────────────────────────────────────────────────────
app.get("/api/dashboard-data", (req, res) => {

  const file = path.join(__dirname, "../results/dashboard_data.json")

  if (!fs.existsSync(file)) {
    return res.json({
      attack_probability:    0,
      predicted_zone:       -1,
      ensemble_auc:          0,
      precision:             0,
      recall:                0,
      f1_score:              0,
      detection_rate:        0,
      total_samples:         0,
      total_attacks_detected: 0
    })
  }

  try {
    const data = JSON.parse(fs.readFileSync(file, "utf8"))
    res.json(data)
  } catch (err) {
    console.error("Failed to parse dashboard_data.json:", err)
    res.status(500).json({ msg: "Failed to read dashboard data" })
  }

})

// ── GradCAM file list (used by GradCAMViewer component) ──────────────────────
app.get("/api/gradcam-files", (req, res) => {

  const dir = path.join(__dirname, "../results/gradcam_examples")

  if (!fs.existsSync(dir)) {
    return res.json({ files: [] })
  }

  try {
    const files = fs.readdirSync(dir)
      .filter(f => f.endsWith(".png"))
      .sort()
    res.json({ files })
  } catch (err) {
    console.error("Failed to read gradcam_examples dir:", err)
    res.json({ files: [] })
  }

})

const PORT = process.env.PORT || 5000

app.listen(PORT, () => {
  console.log(`FDIA dashboard API running on port ${PORT}`)
})