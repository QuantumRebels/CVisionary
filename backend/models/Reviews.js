import mongoose  from "mongoose";

const ReviewSchema=new mongoose.Schema({
    userId:{
        type:String,
        required:true,
        unique:true
    },
    UserName:{
        type:String,
        required:true
    },
    reviewText:{
        type:String,
        required:true
    }
})

const Review=new mongoose.model("Review",ReviewSchema)
export default Review;