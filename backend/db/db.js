import mongoose from "mongoose";
import dotenv from "dotenv";

const connectToDB = async () => {
  try {
    try {
      await mongoose.connect(process.env.MONGO_URL);
      console.log("Connected to Database succesfully");
    }
    catch (error) {
      console.log(error);
      console.log("Database connection failed");
    }
  }
  catch (error) {
    console.log(error);
  }
}

export default connectToDB