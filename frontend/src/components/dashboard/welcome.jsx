import React, { useState, useEffect } from "react";
import { Plus, Wand2 } from "lucide-react";
import { motion } from "framer-motion";

const WelcomeSection = ({ darkMode }) => {
  const [userName, setUserName] = useState("");

  useEffect(() => {
    const storedName = localStorage.getItem("userName");
    if (storedName) setUserName(storedName);
  }, []);

  return (
    <section
      className={`w-full py-16 px-4 md:px-10 mt-12 ${
        darkMode
          ? "bg-[#0d0b22] text-white"
          : "bg-white text-[#18181b]"
      }`}
    >
      <div className="max-w-4xl mx-auto text-center">
        <h1 className="text-4xl md:text-5xl font-bold mb-4 leading-tight">
          Welcome to CVisionary{userName && `, ${userName}`}
        </h1>
        <p className={`text-lg md:text-xl mb-8 ${
          darkMode ? "text-gray-400" : "text-gray-600"
        }`}>
          Craft a standout resume that showcases your skills and helps you land your dream job.
        </p>
        <div className={`flex items-center justify-between max-w-2xl mx-auto gap-3 rounded-full px-6 py-3 transition-all duration-300
          ${darkMode
            ? "bg-[#1a1735] border border-gray-700 shadow-[0_0_15px_rgba(59,130,246,0.3)]"
            : "bg-gray-100 border border-gray-200 shadow-[0_0_15px_rgba(59,130,246,0.1)]"
          }
        `}>
          <Plus className={`w-5 h-5 ${darkMode ? "text-gray-400 hover:text-white" : "text-gray-500 hover:text-blue-600"} transition-colors duration-300 cursor-pointer`} />
          <input
            type="text"
            placeholder="Type your question or request here..."
            className={`flex-grow bg-transparent outline-none text-sm ${
              darkMode
                ? "text-white placeholder:text-blue-400"
                : "text-gray-900 placeholder:text-blue-500"
            } placeholder:animate-pulse`}
          />
          <Wand2 className={`w-5 h-5 ${darkMode ? "text-blue-500 hover:text-white" : "text-blue-600 hover:text-blue-800"} transition-colors duration-300 cursor-pointer`} />
        </div>
      </div>
    </section>
  );
};

export default WelcomeSection;
