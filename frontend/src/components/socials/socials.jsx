import React, { useState, useEffect } from "react";
import { FaGithub, FaLinkedin } from "react-icons/fa";
import { useNavigate } from "react-router-dom";

const SocialConnect = ({ darkMode }) => {
  const navigate = useNavigate();
  const [userName, setUserName] = useState("");

  useEffect(() => {
    const storedName = localStorage.getItem("userName");
    if (storedName) setUserName(storedName);
  }, []);

  // Theme classes
  const bgClass = darkMode ? "bg-[#0D0C1D]" : "bg-white";
  const textClass = darkMode ? "text-white" : "text-gray-900";
  const subTextClass = darkMode ? "text-gray-300" : "text-gray-600";
  const btnBg = darkMode ? "bg-[#1E1B3A]" : "bg-blue-100";
  const btnText = darkMode ? "text-white" : "text-blue-900";
  const btnShadow = darkMode
    ? "shadow-[0_0_10px_rgba(99,102,241,0.4)] hover:shadow-[0_0_20px_rgba(99,102,241,0.8)]"
    : "shadow-[0_0_10px_rgba(59,130,246,0.15)] hover:shadow-[0_0_20px_rgba(30,41,59,0.45)]";
  const btnHover = "hover:scale-105";
  const dashboardBtn = darkMode
    ? "bg-blue-600 hover:bg-blue-700 text-white"
    : "bg-blue-500 hover:bg-blue-600 text-white";

  return (
    <div className={`min-h-screen flex flex-col items-center justify-center ${bgClass} ${textClass} px-4 transition-colors duration-300`}>
      {/* Go to Dashboard Button */}
      <div className="absolute top-24 right-6">
        <button
          onClick={() => navigate("/dashboard")}
          className={`${dashboardBtn} font-semibold py-2 px-6 rounded-lg transition-colors duration-300`}
        >
          Go to Dashboard
        </button>
      </div>

      {/* Welcome Heading */}
      <h1 className="text-4xl md:text-5xl font-bold mb-2 text-center leading-tight">
        Hey {userName && `, ${userName}`}
      </h1>

      <h2 className={`text-xl md:text-2xl ${subTextClass} text-center mb-8`}>
        Are You ready to Generate the Best Personalised Resume?
      </h2>

      {/* Buttons Section */}
      <div className="space-y-6 w-full max-w-md">
        {/* GitHub Button */}
        <button
          onClick={() => navigate("/socials/github")}
          className={`${btnBg} w-full py-4 rounded-2xl ${btnText} font-semibold flex items-center justify-center gap-3 transition duration-300 ease-in-out ${btnShadow} transform ${btnHover}`}
        >
          <FaGithub size={20} /> Connect To GitHub
        </button>

        <p className={`text-sm ${subTextClass} text-center -mt-3`}>
          Connect your GitHub profile with for Github Scrapping
        </p>

        {/* LinkedIn Button */}
        <button
          onClick={() => navigate("/socials/linkedin")}
          className={`${btnBg} w-full py-4 rounded-2xl ${btnText} font-semibold flex items-center justify-center gap-3 transition duration-300 ease-in-out ${btnShadow} transform ${btnHover}`}
        >
          <FaLinkedin size={20} /> Upload LinkedIn PDF
        </button>

        <p className={`text-sm ${subTextClass} text-center -mt-3`}>
          Upload your latest LinkedIn resume in PDF format.
        </p>
      </div>
    </div>
  );
};

export default SocialConnect;
