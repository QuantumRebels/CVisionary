
import Resume from "../models/resume.js";
import Auth from "../models/auth_user.js";

const buildResume = async (req, res) => {
  const {
    userId,
    name,
    email,
    phone_number,
    headline,
    location,
    summary,
    skills,
  } = req.body;

 

  const {
    job_title,
    company_name,
    company_location,
    start_date,
    end_date,
    job_description,
    job_skills,
  } = req.body;

  const { institution_name, degree, start_date1, end_date1, grade } = req.body;

  const { project_name, project_description, project_link, project_skills } =
    req.body;

  const {
    certification_name,
    issuing_organization,
    issue_date,
    expiration_date,
    credential_id,
    credential_url,
  } = req.body;

  const { githubUsername, profile_link } = req.body;

  const { profile_url, connections } = req.body;

   try {
    const user = await Auth.findById(userId);
    if (!user) {
      return res
        .status(404)
        .json({ message: "User not Found . PLease Signup first" });
    } else {
      if (job_title === "Fresher" || job_title === "Student") {
        const newResume = await Resume.create({
          userId,
          name,
          email,
          phone_number,
          headline,
          location,
          summary,
          skills,

          job_title: "Fresher",
          company_name: "N/A",
          company_location: "N/A",
          start_date: "N/A",
          end_date: "N/A",
          job_description: "N/A",
          job_skills: "N/A",

          institution_name,
          degree,
          start_date1,
          end_date1,
          grade,

          project_name,
          project_description,
          project_link,
          project_skills,

          certification_name,
          issuing_organization,
          issue_date,
          expiration_date,
          credential_id,
          credential_url,

          githubUsername,
          profile_link,
          profile_url,
          connections,
        });

        return res.status(201).json({
          success: true,
          message: "Resume created successfully",
          resume: newResume,
        });
      } else {
        const newResume = await Resume.create({
          userId,
          name,
          email,
          phone_number,
          headline,
          location,
          summary,
          skills,

          job_title,
          company_name,
          company_location,
          start_date,
          end_date,
          job_description,
          job_skills,

          institution_name,
          degree,
          start_date1,
          end_date1,
          grade,

          project_name,
          project_description,
          project_link,
          project_skills,

          certification_name,
          issuing_organization,
          issue_date,
          expiration_date,
          credential_id,
          credential_url,

          githubUsername,
          profile_link,
          profile_url,
          connections,
        });
        return res.status(201).json({
          success: true,
          message: "Resume created successfully",
          resume: newResume,
        });
      }
    }
  } catch (error) {
    return res.status(500).json({
      success: false,
      message: "Internal Server Error",
      error: error.message,
    });
  }


};
const getResumes=async(req,res)=>{
  const {UserId}=req.body;

  try {
    const resumes=await Resume.find({userId:UserId});
    if(resumes.length===0){
     return res.status(404).json({message:"No resumes Found"});
    }else{
     return res.status(200).json({message:"Resumes Found",resumes:resumes});
    }
  } catch (error) {
    return res.status(500).json({
      message:"Internal Server Error",
      error:error.message
    })
    
  }
}

export default {buildResume,getResumes};
