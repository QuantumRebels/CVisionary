import mongoose  from "mongoose";

const JobSchema = new mongoose.Schema({
     userId : {
      type : mongoose.Schema.Types.ObjectId,
      ref: "Auth_User",
      required : true ,
     },
     JobTitle : {
      type : String ,
      required : true ,
     },
     JobDescription : {
      type : String ,
      required : true ,
     },
     CompanyName : {
      type : String ,
      required : true ,
     },
     Location : {
      type : String ,
      required : true 
     },
     Cateogory : {
      type : [String]
     },
     JobType : {
      type : String ,
      required : true 
     },
     Stipend:{
          type : String ,
          required : true
     }
     
})

const Job = mongoose.model("Job",JobSchema);

export default Job;