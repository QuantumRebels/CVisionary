import { Router } from "express";
import { githubScrapper } from "../controllers/SocialConnectController.js";

const ScrapperRouter=Router()

ScrapperRouter.get("/github",githubScrapper)

export default ScrapperRouter;