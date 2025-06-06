import User from '../models/auth_user.js';
import bycrypt from 'bcryptjs'

const registerUser = async (req, res) => {
  const { username, useremail, userpassword } = req.body;
  try {
    try {

      const checkuserEmail = await User.findOne({ userEmail: useremail });
      if (checkuserEmail) {
        return res.status(404).json({
          success: false,
          message: "Email already exists",
        })
      }
      const checkuserName = await User.findOne({ userName: username });
      if (checkuserName) {
        return res.status(404).json({
          success: false,
          message: " Username already exists",
        })
      }

      const salt = await bycrypt.genSalt(10);
      const hashedPassword = await bycrypt.hash(userpassword, salt);

      const newUser = await User.create({
        userName : username,
        userEmail : useremail,
        userPassword : hashedPassword,
      })
      
      if(newUser){
        return res.status(201).json({
          success : true ,
          message : "User registered successfully"
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

export default  registerUser ;