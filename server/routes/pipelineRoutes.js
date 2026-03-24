require("dotenv").config()

const express = require("express")
const router = express.Router()
const auth = require("../middleware/auth")
const { spawn } = require("child_process")
const path = require("path")

// Track pipeline state in memory
let pipelineStatus = {
  running: false,
  lastStatus: "idle",   // idle | running | success | error
  lastMessage: "",
  lastRun: null
}

// ---------------------------------------------------
// GET /api/pipeline/status
// Frontend polls this to know when pipeline finishes
// ---------------------------------------------------
router.get("/status", auth, (req, res) => {
  res.json(pipelineStatus)
})

// ---------------------------------------------------
// GET /api/pipeline/run
// Starts the Python pipeline
// ---------------------------------------------------
router.get("/run", auth, (req, res) => {

  if (pipelineStatus.running) {
    return res.status(409).json({ msg: "Pipeline is already running" })
  }

  const pythonPath = process.env.PYTHON_PATH || "python"
  const projectRoot = process.env.PROJECT_ROOT || path.join(__dirname, "../../")

  pipelineStatus = {
    running: true,
    lastStatus: "running",
    lastMessage: "Pipeline started",
    lastRun: new Date().toISOString()
  }

  const pythonProcess = spawn(
    pythonPath,
    ["main.py"],
    { cwd: projectRoot }
  )

  pythonProcess.stdout.on("data", (data) => {
    console.log(`PYTHON: ${data}`)
    pipelineStatus.lastMessage = data.toString().trim()
  })

  pythonProcess.stderr.on("data", (data) => {
    console.error(`PYTHON ERROR: ${data}`)
  })

  pythonProcess.on("close", (code) => {
    console.log(`Python process finished with code ${code}`)
    pipelineStatus.running = false

    if (code === 0) {
      pipelineStatus.lastStatus = "success"
      pipelineStatus.lastMessage = "Pipeline completed successfully"
    } else {
      pipelineStatus.lastStatus = "error"
      pipelineStatus.lastMessage = `Pipeline failed with exit code ${code}`
    }
  })

  // Respond immediately — frontend polls /status for completion
  res.json({ msg: "Pipeline started" })

})

module.exports = router