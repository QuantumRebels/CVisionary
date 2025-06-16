import React, { useState, useEffect } from "react";
import { FaGithub, FaLinkedin } from "react-icons/fa";
import { useNavigate } from "react-router-dom";

const SocialConnect = () => {
  const navigate = useNavigate();
  const [userName, setUserName] = useState("");

  useEffect(() => {
    const storedName = localStorage.getItem("userName");
    if (storedName) setUserName(storedName);
  }, []);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-[#0D0C1D] text-white px-4">
      {/* Go to Dashboard Button */}
      <div className="absolute top-24 right-6">
        <button
          onClick={() => navigate("/dashboard")}
          className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg"
        >
          Go to Dashboard
        </button>
      </div>

      {/* Welcome Heading */}
      <h1 className="text-4xl md:text-5xl font-bold mb-2 text-center leading-tight">
        Hey {userName && `, ${userName}`}
      </h1>
      <h2 className="text-xl md:text-2xl text-gray-300 text-center mb-8">
        Are You ready to Generate the Best Personalised Resume?
      </h2>

      {/* Buttons Section */}
      <div className="space-y-6 w-full max-w-md">
        {/* GitHub Button */}
        <button
          onClick={() => navigate("/socials/github")}
          className="bg-[#1E1B3A]  w-full py-4 rounded-2xl text-white font-semibold flex items-center justify-center gap-3 transition duration-300 ease-in-out shadow-[0_0_10px_rgba(99,102,241,0.4)] hover:shadow-[0_0_20px_rgba(99,102,241,0.8)] transform hover:scale-105"
        >
          <FaGithub size={20} /> Connect To GitHub
        </button>
        <p className="text-sm text-gray-400 text-center -mt-3">
          Connect your GitHub profile with for Github Scrapping
        </p>

        {/* LinkedIn Button */}
        <button
          onClick={() => navigate("/socials/linkedin")}
          className="bg-[#1E1B3A]  w-full py-4 rounded-2xl text-white font-semibold flex items-center justify-center gap-3 transition duration-300 ease-in-out shadow-[0_0_10px_rgba(99,102,241,0.4)] hover:shadow-[0_0_20px_rgba(99,102,241,0.8)] transform hover:scale-105"
        >
          <FaLinkedin size={20} /> Upload LinkedIn PDF
        </button>
        <p className="text-sm text-gray-400 text-center -mt-3">
          Upload your latest LinkedIn resume in PDF format.
        </p>
      </div>
    </div>
  );
};

export default SocialConnect;
