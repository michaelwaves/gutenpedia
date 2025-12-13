const express = require('express')
const cors = require("cors")
const app = express();
const corsOptions = {
    origin: ["http://localhost:5173"]
}
app.use(cors(corsOptions))

app.get("/api", (req, res) => {
    console.log(req)
    res.json({ "fruits": ["apple", "pear", "pineapple"] })
})

app.listen(8001, () => {
    "server started on port 8001"
})