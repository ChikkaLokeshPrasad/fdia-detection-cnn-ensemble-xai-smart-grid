require("dotenv").config()

const jwt = require("jsonwebtoken")

module.exports = function (req, res, next) {

  const token = req.headers.authorization

  if (!token) return res.status(401).json({ msg: "Unauthorized" })

  try {

    const secret = process.env.JWT_SECRET || "fdia_secret"
    const decoded = jwt.verify(token, secret)
    req.user = decoded
    next()

  } catch (err) {

    res.status(401).json({ msg: "Invalid token" })

  }

}