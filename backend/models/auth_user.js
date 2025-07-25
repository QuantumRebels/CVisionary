import mongoose from "mongoose";

const UserSchema = new mongoose.Schema({
  userName: {
    type: String,
    required: true,
    unique: true
  },
  userEmail: {
    type: String,
    required: true,
    unique: true,
  },
  userPassword : {
    type : String ,
    required : true ,
  },
  userImage: {
    type : String ,
    default : "https://res.cloudinary.com/dz1qj3x8h/image/upload/v1709308700/Default-Profile-Picture"
  }
})

const Auth = mongoose.model("Auth_User", UserSchema);

export default Auth;

