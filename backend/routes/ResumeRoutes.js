
import { Router } from 'express';
import {buildResume ,getResumes}from '../controllers/ResumeController.js';

const ResumeRouter=Router();

ResumeRouter.post('/build',buildResume)
ResumeRouter.get('/getresumes',getResumes);


export default ResumeRouter