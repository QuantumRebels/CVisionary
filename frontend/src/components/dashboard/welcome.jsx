import React from "react";
import { Plus, Wand2 } from "lucide-react";

const WelcomeSection = () => {
  return (
    <section className="w-full bg-[#0d0b22] text-white py-16 px-4 md:px-10 mt-12">
      <div className="max-w-4xl mx-auto text-center">
        {/* Heading */}
        <h1 className="text-4xl md:text-5xl font-bold mb-4 leading-tight">
          Welcome to CVisionary
        </h1>

        {/* Subtext */}
        <p className="text-gray-400 text-lg md:text-xl mb-8">
          Craft a standout resume that showcases your skills and helps you land your dream job.
        </p>

        {/* Input Box with Always-On Glow */}
        <div className="flex items-center justify-between max-w-2xl mx-auto gap-3 bg-[#1a1735] border border-gray-700 shadow-[0_0_15px_rgba(59,130,246,0.3)] rounded-full px-6 py-3 transition-all duration-300">
          <Plus className="w-5 h-5 text-gray-400 hover:text-white transition-colors duration-300 cursor-pointer" />
          <input
            type="text"
            placeholder="Type your question or request here..."
            className="flex-grow bg-transparent outline-none text-sm text-white placeholder:text-blue-400 placeholder:animate-pulse"
          />
          <Wand2 className="w-5 h-5 text-blue-500 hover:text-white transition-colors duration-300 cursor-pointer" />
        </div>
      </div>
    </section>
  );
};

export default WelcomeSection;
