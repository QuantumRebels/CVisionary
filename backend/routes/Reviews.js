import { Router } from "express";

const ReviewsRouter=Router();
import {writeReview, getReviews} from '../controllers/ReviewsController.js';

ReviewsRouter.post("/write", writeReview);
ReviewsRouter.get("/getreviews", getReviews);

export default ReviewsRouter;