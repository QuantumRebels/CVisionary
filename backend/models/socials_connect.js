const mongoose = require("mongoose");

// Schema for connecting social accounts to the user
const SocialsConnectSchema = new mongoose.Schema({

  // Reference to the user in the Auth_User collection
   userId: {
    type : mongoose.Schema.Types.ObjectId,
    ref : "Auth_User",
    required : true 
   },

    // Social provider information to which the user is connecting
   socialProvider : {
    type : String ,
    enum : ["LinkedIn", "GitHub"],
    required : true
   },

    // Unique identifier for the social provider account to which the user is connecting
   socialProviderId : {
    type : String,
   },

   // Tokens for accessing the social provider's API
   accessToken : {
    type : String
   },

   // Refresh token for renewing access tokens so that the user does not have to re-authenticate frequently
   refreshToken : {
    type : String
   },

   // Data scrapped from the social provider, such as profile information
   scrappedData : {
    type : Object,
    default : {},
   },

   // Timestamp for when the user connected their social account
   connectedAt :{
    type : Date ,
    default: Date.now()
   }
  },
   {timestamps: true} // Automatically manage createdAt and updatedAt fields
);

module.exports = mongoose.model("Socials_Connect", SocialsConnectSchema);
