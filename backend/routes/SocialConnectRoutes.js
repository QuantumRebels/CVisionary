import { Router } from "express";
import {  githubRepo, githubScrapper } from "../controllers/SocialConnectController.js";

const ScrapperRouter=Router()

ScrapperRouter.get("/github",githubScrapper)
ScrapperRouter.get("/github/repos",githubRepo)


export default ScrapperRouter;