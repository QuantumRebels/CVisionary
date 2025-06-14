import Review from "../models/Reviews.js";

const writeReview=async(req,res)=>{
    const {userId , UserName, reviewText} = req.body;
    try {
        const newReview = await Review.create({
            userId,
            UserName,
            reviewText
        });
        return res.status(201).json({
            success: true,
            message: "Review added successfully",
            data: newReview
        });
    } catch (error) {
        console.error(error);
        return res.status(500).json({
            success: false,
            message: "Internal Server Error"
        });
    }
}

const getReviews=async(req,res)=>{
    try {
        const reviews=await Review.find()
        if(reviews.length===0){
            return res.status(404).json({
                success: false,
                message: "No reviews found"
            });
        }else{
            return res.status(200).json({
                message:"Success",
                reviews:reviews
            })
        }
    } catch (error) {
        console.error(error);
        return res.status(500).json({
            success: false,
            message: "Internal Server Error"
        });
    }
}

export  {writeReview, getReviews};