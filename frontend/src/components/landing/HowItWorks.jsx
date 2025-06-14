import React, { useState } from "react";
import { motion } from "framer-motion";
import Thumbnail from "../../assets/images/thumbnail.jpg"; // Replace with your actual thumbnail image

function HowItWorks() {
  const [playVideo, setPlayVideo] = useState(false);

  // Animation variants for the step list
  const containerVariants = {
    hidden: {},
    visible: {
      transition: {
        staggerChildren: 0.3,
      },
    },
  };

  const stepVariants = {
    hidden: { opacity: 0, x: -30 },
    visible: {
      opacity: 1,
      x: 0,
      transition: {
        duration: 0.6,
        ease: "easeOut",
      },
    },
  };

  return (
    <section className="mt-8 mb-8 px-6 md:px-12"  id="how-it-works">
      <motion.h2
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        viewport={{ once: true, amount: 0.3 }}
        className="text-4xl font-bold text-center mt-12 text-white mb-8"
      >
        How It Works
      </motion.h2>

      <div className="flex flex-col lg:flex-row items-start justify-between gap-12">
        {/* Left Text Section */}
        <motion.div
          className="lg:w-1/2 mt-6 ml-10"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6 }}
        >
          <p className="text-[#d6d6dd] mb-6 font-semibold text-lg">
            Unlock your dream career in just three simple steps! Our intelligent platform does the heavy lifting so you can focus on what matters—landing your next big opportunity.
          </p>

          <motion.div
            className="flex flex-col gap-6"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.3 }}
            variants={containerVariants}
          >
            {["Scrape", "JD Match", "Resume Generate"].map((step, i) => (
              <motion.div
                key={i}
                className="flex items-start gap-2"
                variants={stepVariants}
              >
                <span className="text-[#b3b3c6] font-mono">H<sub>3</sub></span>
                <span className="text-white">
                  <span className="font-semibold">{step}:</span>{" "}
                  {step === "Scrape"
                    ? "Instantly extract key skills and requirements from any job description."
                    : step === "JD Match"
                    ? "Our AI matches your strengths to the perfect roles—no more guesswork."
                    : "Get a polished, ATS-friendly resume in seconds, ready to impress any recruiter."}
                </span>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>

        {/* Right YouTube Embed or Thumbnail */}
        <motion.div
          className="lg:w-1/2 w-full flex justify-center mt-6"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
        >
          <div className="w-full max-w-xl rounded-xl overflow-hidden shadow-lg ring-1 ring-[#2a2a45]">
            <div className="aspect-video w-full relative">
              {!playVideo ? (
                <div
                  className="w-full h-full bg-black cursor-pointer group"
                  onClick={() => setPlayVideo(true)}
                >
                  <img
                    src={Thumbnail}
                    alt="Video Thumbnail"
                    className="w-full h-full object-cover group-hover:brightness-90 transition-all duration-300"
                  />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="bg-white text-black px-4 py-2 rounded-full font-semibold shadow-md hover:scale-105 transition-all">
                      ▶ Watch Demo
                    </div>
                  </div>
                </div>
              ) : (
                <iframe
                  className="w-full h-full"
                  src="https://www.youtube.com/embed/WQwLZ70RWFg"
                  title="How It Works Demo"
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                ></iframe>
              )}
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

export default HowItWorks;
