import User from '../models/auth_user.js';
import bycrypt from 'bcryptjs'
import jwt from 'jsonwebtoken';
import dotenv from 'dotenv';


const registerUser = async (req, res) => {
  const { username, useremail, userpassword } = req.body;
  try {
    try {

      const checkuserEmail = await User.findOne({ userEmail: useremail });
      if (checkuserEmail) {
        return res.status(400).json({
          success: false,
          message: "Email already exists",
        })
      }
      const checkuserName = await User.findOne({ userName: username });
      if (checkuserName) {
        return res.status(400).json({
          success: false,
          message: " Username already exists",
        })
      }

      const salt = await bycrypt.genSalt(10);
      const hashedPassword = await bycrypt.hash(userpassword, salt);

      const newUser = await User.create({
        userName: username,
        userEmail: useremail,
        userPassword: hashedPassword,
      })

      // const accessToken = jwt.sign({
      //   username : username,
      //   userId :_id,
      //   useremail : useremail
      // } ,
      //  process.env.JWT_SECRET, 
      //  {expiresIn: '1d'}
      // );

      if (newUser) {
        return res.status(201).json({
          success: true,
          message: "User registered successfully",
          // accessToken: accessToken
        })
      }
    }
    catch (error) {
      console.log(error);
      return res.status(400).json({
        success: false,
        message: "User is not registered",
      })
    }
  }

  catch (error) {
    console.log(error);
    return res.status(500).json({
      success: false,
      message: "Internal Server Error",
    })
  }
}

const loginController = async (req, res) => {
  try {
    try {
      const { useremail, userpassword } = req.body;
      
      const checkuser = await User.findOne({ userEmail: useremail });
      
      if (!checkuser) {
        return res.status(404).json({
          success: false,
          message: "User Not Found"
        })
      }
      const checkPassword = await bycrypt.compare(userpassword, checkuser.userPassword)
      if (!checkPassword) {
        return res.status(401).json({
          success: false,
          message: "Invalid Password"
        })
      }

      const accessToken = jwt.sign({
        username : checkuser.userName,
        userId : checkuser._id,
        useremail : checkuser.userEmail
      } ,
       process.env.JWT_SECRET, 
       {expiresIn: '1d'}
      );

      return res.status(200).json({
        success : true ,
        message: "User logged in successfully",
        accessToken : accessToken,
        user : checkuser
      })
      

    }
    catch (error) {
      console.log(error);
      return res.status(400).json({
        success: false,
        message: "User is not logged in "
      })
    }
  }
  catch (error) {
    console.log(error);
    return res.status(500).json({
      success: false,
      message: "Internal Server Error"
    })
  }
}




export  { registerUser , loginController };