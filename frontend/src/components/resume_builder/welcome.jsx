// components/Welcome.jsx
import { useState } from "react";
import { useEffect } from "react";
import React from "react";

const Welcome = ({ onPromptSubmit }) => {
  const [input, setInput] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() !== "") onPromptSubmit(input);
  };

  const [userName, setUserName] = useState("");

  useEffect(() => {
    const storedName = localStorage.getItem("userName");
    if (storedName) setUserName(storedName);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center h-screen text-center space-y-6 bg-[#0d0b22] text-white">
      <h1 className="text-3xl md:text-4xl font-bold mb-4 leading-tight">
        Hey{userName && `, ${userName}`} ! Start crafting your resume
      </h1>
      <p className="text-[#a0a3b1] text-lg max-w-xl">
        Let’s build your resume. Build your resume with AI assistance.
      </p>
      <form onSubmit={handleSubmit} className="flex space-x-4">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your initial prompt here..."
          className="px-4 py-2 rounded-md bg-[#1c1f2a] text-white border border-[#2a2d3e] w-96 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          className="bg-blue-600 px-6 py-2 rounded-md hover:opacity-90 transition"
        >
          Start
        </button>
      </form>
    </div>
  );
};

export default Welcome;