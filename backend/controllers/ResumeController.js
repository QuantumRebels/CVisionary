import express from "express";
import Resume from "../models/resume.js";

const buildResume = (req, res) => {
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


  const {institution_name,
      degree,
      start_date1,
      end_date1,
      grade}=req.body;

    const {project_name,
      project_description,
      project_link,
      project_skills}=req.body;

    const {certification_name,
      issuing_organization,
      issue_date,
      expiration_date,
      credential_id,
      credential_url}=req.body;

    const {githubUsername,
    profile_link}=req.body;

    const {profile_url,
    connections}=req.body;

    

};


export default buildResume