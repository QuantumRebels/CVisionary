import mongoose from "mongoose";

const ResumeSchema = new mongoose.Schema({
  userId: {
    type:String
  },
  name: {
    type: String
  },
  email: {
    type: String
  },
  phone_number: {
    type: String
  },
  headline: {
    type: String
  },
  location: {
    type: String
  },
  summary: {
    type: String
  },

  skills: {
    type: [String]
  },

  experiences: [
    {
      job_title: {
        type: String,
      },
      company_name: {
        type: String,
      },
      company_location: {
        type: String,
      },
      start_date: {
        type: Date,
      },
      end_date: {
        type: Date,
      },
      job_description: {
        type: String,
      },
      job_skills: {
        type: [String],
      }
    }
  ],

  education: [
    {
      institution_name: {
        type: String,
      },
      degree: {
        type: String,
      },
      start_date: {
        type: Date,
      },
      end_date: {
        type: Date,
      },
      grade: {
        type: String,
      }
    }
  ],

  projects: [
    {
      project_name: {
        type: String,
      },
      project_description: {
        type: String,
      },
      project_link: {
        type: String,
      },
      project_skills: {
        type: [String],
      }
    }
  ],

  certifications: [
    {
      certification_name: {
        type: String,
      },
      issuing_organization: {
        type: String,
      },
      issue_date: {
        type: Date,
      },
      expiration_date: {
        type: Date,
      },
      credential_id: {
        type: String,
      },
      credential_url: {
        type: String,
      }
    }
  ],

  github: {
    username: {
      type: String,
    },
    profile_link: {
      type: String,
    },
    repos: [
      {
        repo_name: {
          type: String,
        },
        repo_description: {
          type: String,
        },
        repo_link: {
          type: String,
        },
        repo_language: {
          type: String,
        },
        stars: {
          type: Number,
        },
        forks: {
          type: Number,
        }
      }
    ]
  },

  linkedin: {
    profile_url: {
      type: String,
    },
    connections: {
      type: Number
    }
  },

  lastupdated :{
    type : Date,
    default:Date.now(),
  }
 
} , { timestamps:true}
)

const Resume = mongoose.model("Resume", ResumeSchema);

export default Resume;