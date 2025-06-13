import React from "react";

function HowItWorks() {
  return (
    <section className="mt-8 mb-8">
      <h2 className="text-xl font-semibold text-white mb-4 pl-8">How It Works</h2>
      <div className="pl-16">
        <p className="text-[#b3b3c6] mb-6 max-w-xl">
          Unlock your dream career in just three simple steps! Our intelligent platform does the heavy lifting so you can focus on what matters—landing your next big opportunity. Fast, precise, and tailored for you.
        </p>
        <div className="flex flex-col gap-6">
          <div className="flex items-start gap-2">
            <span className="text-[#b3b3c6] font-mono">H<sub>3</sub></span>
            <span className="text-white">
              <span className="font-semibold">Scrape:</span> Instantly extract key skills and requirements from any job description.
            </span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-[#b3b3c6] font-mono">H<sub>3</sub></span>
            <span className="text-white">
              <span className="font-semibold">JD Match:</span> Our AI matches your strengths to the perfect roles—no more guesswork.
            </span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-[#b3b3c6] font-mono">H<sub>3</sub></span>
            <span className="text-white">
              <span className="font-semibold">Resume Generate:</span> Get a polished, ATS-friendly resume in seconds, ready to impress any recruiter.
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}

export default HowItWorks;