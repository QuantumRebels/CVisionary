require("dotenv").config() ;

const express = require("express");

const connectToDB = require("./db/db")

const app = express();
app.use(express.json());
const PORT = process.env.PORT ;

connectToDB();


app.listen(PORT , () => {
  console.log(`Server is running successfully on ${PORT}`);
})