import dotenv from "dotenv";
import express from "express";

import connectToDB from "./db/db.js";
import authRoutes from "./routes/UserRoutes.js";
import cookieParser from 'cookie-parser';
import ResumeRouter from "./routes/ResumeRoutes.js";
import ReviewsRouter from "./routes/Reviews.js";
import JobRouter from "./routes/JobRoutes.js";

dotenv.config();

const app = express();
app.use(express.json());
app.use(cookieParser());

const PORT = process.env.PORT;

connectToDB();
app.use("/auth", authRoutes)
app.use("/resume", ResumeRouter);
app.use("/review",ReviewsRouter)
app.use("/jobs",JobRouter)

app.listen(PORT, () => {
  console.log(`Server is running successfully on ${PORT}`);
});

