import dotenv from "dotenv";
import express from "express";
import cors from "cors";  

import connectToDB from "./db/db.js";
import UserRouter from "./routes/UserRoutes.js";
import cookieParser from 'cookie-parser';
import ResumeRouter from "./routes/ResumeRoutes.js";
import ReviewsRouter from "./routes/Reviews.js";
import JobRouter from "./routes/JobRoutes.js";
import ScrapperRouter from "./routes/SocialConnectRoutes.js";

dotenv.config();

const app = express();
app.use(express.json());
app.use(cookieParser());
app.use(cors({
  origin: "*",
  credentials: true,
  methods: ["GET", "POST", "PUT", "DELETE", "PATCH"],
  allowedHeaders: ["Content-Type", "Authorization", "X-Requested-With"],
}));

const PORT = process.env.PORT;

connectToDB();
app.get('/', (req, res) => {
  res.send('Hello World!!!!')
})

app.use("/auth", UserRouter)
app.use("/resume", ResumeRouter);
app.use("/review",ReviewsRouter)
app.use("/jobs",JobRouter)

app.use("/Scrapper",ScrapperRouter)

app.listen(PORT, () => {
  console.log(`Server is running successfully on ${PORT}`);
});

