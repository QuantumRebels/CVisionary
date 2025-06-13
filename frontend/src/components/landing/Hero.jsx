import React from "react";
import ResumeIllustration from "./ResumeIllustration";

function Hero() {
  return (
    <section className="flex flex-col md:flex-row items-center justify-center md:justify-between px-8 py-12 bg-[#13132a]">
      {/* Illustration */}
      <div className="flex-shrink-0 mb-8 md:mb-0 md:mr-12 md:ml-8">
        <ResumeIllustration />
      </div>
      {/* Text Content */}
      <div className="max-w-xl text-center md:text-left">
        <h1 className="text-4xl md:text-5xl font-extrabold text-white mb-4 leading-tight">
          Your Dream Job, One <br className="hidden md:block" />
          Resume Away
        </h1>
        <p className="text-lg text-[#c7c7d9] mb-8">
          Craft a standout resume with our AI-powered tools. Match your skills
          to job descriptions, generate professional resumes, and land your
          dream job.
        </p>
        <div className="flex flex-col md:flex-row gap-4 justify-center md:justify-start">
          <button className="bg-[#2563eb] hover:bg-[#1d4ed8] text-white px-6 py-2 rounded-md font-medium transition-colors">
            Login with GitHub
          </button>
          <button className="bg-[#23233a] hover:bg-[#35355c] text-white px-6 py-2 rounded-md font-medium transition-colors">
            Login with LinkedIn
          </button>
        </div>
      </div>
    </section>
  );
}

export default Hero;