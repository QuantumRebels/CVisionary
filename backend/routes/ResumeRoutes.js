import express from 'express';

import { Router } from 'express';
import buildResume from '../controllers/ResumeController.js';

const ResumeRouter=Router();

ResumeRouter.post('/build',buildResume)

export default ResumeRouter