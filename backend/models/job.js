import mongoose  from "mongoose";

const JobSchema = new mongoose.Schema({
     userId : {
      type : Mongoose.Schema.Types.ObjectId,
      ref: "Auth_User",
      required : true ,
     },
     JobTitle : {
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
     createdAt : {
      tyep : Date ,
      default : Date.now()
     }
})

const Job = mongoose.model("Job",JobSchema);

export default Job;