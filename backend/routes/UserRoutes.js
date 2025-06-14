import { Router } from "express";

import {registerUser, loginController}  from "../controllers/auth.js";
import Auth_User from "../models/auth_user.js";

const UserRouter = Router();

UserRouter.post("/register" , registerUser);
UserRouter.post("/login", loginController);
UserRouter.get("/getusers", async (req, res) => {
    const users=await Auth_User.find();
    return res.status(200).json({users:users,message:"User Found"})
})



export default UserRouter;