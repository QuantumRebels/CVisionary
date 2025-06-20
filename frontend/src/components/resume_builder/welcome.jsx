import { useState, useEffect } from "react";
import React from "react";

const Welcome = ({ onPromptSubmit, darkMode }) => {
  const [input, setInput] = useState("");
  const [userName, setUserName] = useState("");

  useEffect(() => {
    const storedName = localStorage.getItem("userName");
    if (storedName) setUserName(storedName);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() !== "") onPromptSubmit(input);
  };

  const bgClass = darkMode ? "bg-[#0d0b22]" : "bg-white";
  const textClass = darkMode ? "text-white" : "text-gray-900";
  const subTextClass = darkMode ? "text-[#a0a3b1]" : "text-gray-600";
  const inputBg = darkMode
    ? "bg-[#1c1f2a] text-white border-[#2a2d3e]"
    : "bg-blue-100 text-gray-900 border-blue-200";
  const inputFocus = darkMode
    ? "focus:ring-blue-500"
    : "focus:ring-blue-600";
  const btnBg = darkMode
    ? "bg-blue-600 text-white"
    : "bg-blue-500 text-white hover:bg-blue-600";

  return (
    <div className={`flex flex-col items-center justify-center h-screen text-center space-y-6 ${bgClass} ${textClass} transition-colors duration-300`}>
      <h1 className="text-3xl md:text-4xl font-bold mb-4 leading-tight">
        Hey{userName && `, ${userName}`} ! Start crafting your resume
      </h1>
      <p className={`text-lg max-w-xl ${subTextClass}`}>
        Let’s build your resume. Build your resume with AI assistance.
      </p>
      <form onSubmit={handleSubmit} className="flex space-x-4">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your initial prompt here..."
          className={`px-4 py-2 rounded-md ${inputBg} border w-96 focus:outline-none ${inputFocus}`}
        />
        <button
          type="submit"
          className={`${btnBg} px-6 py-2 rounded-md hover:opacity-90 transition`}
        >
          Start
        </button>
      </form>
    </div>
  );
};

export default Welcome;