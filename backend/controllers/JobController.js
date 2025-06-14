import Job from "../models/job"


const postJob=async(req,res)=>{
    const {userId , JobTitle ,JobDescription, CompanyName , Location , Category  , JobType , Stipend }=req.body

    try {
        const newJob= await Job.create({
            userId,
            JobTitle,
            JobDescription,
            CompanyName,
            Location,
            Category,
            JobType,
            Stipend
        })
        return res.status(201).json({
            success: true,
            message: "Job posted successfully",
            job: newJob
        })
    } catch (error) {
        console.error(error);
        return res.status(500).json({
            success: false,
            message: "Internal Server Error"
        });
    }
}

const getAllJobs =async(req,res)=>{
    try {
        const jobs=await Job.find().sort({ createdAt: -1 });
       return res.status(200).json({
           success: true,
           message: "Jobs fetched successfully",
           jobs
       });
    } catch (error) {
        console.error(error);
        return res.status(500).json({
            success: false,
            message: "Internal Server Error"
        });
    }
}

export default {

    postJob,
    getAllJobs
}