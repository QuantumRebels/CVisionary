import React from "react";
import HeroImage from "../../assets/images/hero.jpg";
import { motion } from "framer-motion";

function Hero() {
  return (
    <section className="flex flex-col md:flex-row items-center justify-center md:justify-between -mt-30 px-8 pt-32 pb-12 bg-[#13132a]">
      {/* Animated Image Container */}
      <motion.div
        initial={{ opacity: 0, x: -50, scale: 0.95 }}
        whileInView={{ opacity: 1, x: 0, scale: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        viewport={{ once: true }}
        className="relative bg-gradient-to-br from-[#1a1a3f] to-[#0f0f2a] p-4 rounded-2xl shadow-[0_0_30px_rgba(0,123,255,0.25)] ring-1 ring-[#1f1f3d] mt-10 ml-16"
      >
        <motion.img
          src={HeroImage}
          alt="Hero Illustration"
          whileHover={{ scale: 1.05 }}
          transition={{ type: "spring", stiffness: 200 }}
          className="w-full max-w-md h-auto rounded-xl"
        />
      </motion.div>

      {/* Text Content */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7 }}
        className="max-w-xl text-center md:text-left mr-12 text-white"
      >
        <h1 className="text-5xl font-extrabold mb-4 leading-tight">
          Your Dream Job, One <br className="hidden md:block" /> Resume Away
        </h1>
        <p className="text-lg text-[#c7c7d9] mb-6">
          AI-crafted, ATS-optimized resumes tailored to match your dream job — all in seconds.
        </p>
        <p className="text-lg text-[#c7c7d9] mb-6">
          Craft your perfect resume effortlessly with our AI-powered platform. Whether you're a seasoned professional or just starting out, we help you stand out in the job market with personalized, ATS-friendly resumes that get results.
        </p>

        <div className="flex flex-col md:flex-row gap-4 justify-center md:justify-start">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-semibold transition-all duration-300 shadow-md hover:shadow-[0_0_12px_rgba(59,130,246,0.5)]"
          >
            🚀 Generate Your Resume
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="bg-[#23233a] hover:bg-[#35355c] text-white px-6 py-2 rounded-lg font-semibold transition-all duration-300 shadow-md hover:shadow-[0_0_12px_rgba(255,255,255,0.15)]"
          >
            🎥 See How It Works
          </motion.button>
        </div>

        <div className="mt-4 text-md text-[#7f7f99]">
          Trusted by <span className="text-white font-semibold">10,000+</span> job seekers • ATS Score Boost: <span className="text-white font-medium">85%</span>
        </div>
      </motion.div>
    </section>
  );
}

export default Hero;
