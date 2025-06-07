import dotenv from "dotenv";
import express from "express";

import connectToDB from "./db/db.js";
import authRoutes from "./routes/routes.js";


dotenv.config();

const app = express();
app.use(express.json());

const PORT = process.env.PORT;

connectToDB();
app.use("/auth", authRoutes)

app.listen(PORT, () => {
  console.log(`Server is running successfully on ${PORT}`);
});

