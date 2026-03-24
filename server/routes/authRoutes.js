require("dotenv").config()

const express = require("express")
const jwt = require("jsonwebtoken")

const router = express.Router()

router.post("/login", (req, res) => {

  const { username, password } = req.body

  const validUser = process.env.ADMIN_USERNAME || "admin"
  const validPass = process.env.ADMIN_PASSWORD || "fdia123"
  const secret    = process.env.JWT_SECRET || "fdia_secret"

  if (username === validUser && password === validPass) {

    const token = jwt.sign(
      { user: "admin" },
      secret,
      { expiresIn: "2h" }
    )

    return res.json({ token })
  }

  res.status(401).json({ msg: "Invalid credentials" })

})

module.exports = router