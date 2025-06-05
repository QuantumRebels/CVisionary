require("dotenv").config();
const mongoose = require("mongoose");

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

module.exports = connectToDB;