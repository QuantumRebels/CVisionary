import { Router } from "express";

import {registerUser, loginController}  from "../controllers/auth.js";

const router = Router();

router.post("/register" , registerUser);
router.post("/login", loginController);



export default router;