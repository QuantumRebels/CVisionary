import { Router } from "express";

import {registerUser, loginController}  from "../controllers/auth.js";

const UserRouter = Router();

UserRouter.post("/register" , registerUser);
UserRouter.post("/login", loginController);



export default UserRouter;