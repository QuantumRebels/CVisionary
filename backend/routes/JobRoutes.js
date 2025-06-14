import {Router} from 'express';
import { postJob , getAllJobs } from '../controllers/JobController.js';

const JobRouter=Router();

JobRouter.post("/create", postJob)
JobRouter.get("/all", getAllJobs);

export default JobRouter;