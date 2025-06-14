import React, { useState } from "react";
import Navbar from "@/components/landing/Navbar";
import HowItWorks from "@/components/landing/HowItWorks";
import Hero from "@/components/landing/Hero";
import Features from "@/components/landing/Features";
import Testimonials from "@/components/landing/Testimonials";
import Footer from "@/components/landing/Footer";

const Landing = () => {
  const [darkMode, setDarkMode] = useState(true);

  return (
    <div className={darkMode ? "bg-[#13132a] min-h-screen" : "bg-white min-h-screen"}>
      <Navbar isLoggedIn={false} darkMode={darkMode} setDarkMode={setDarkMode} />
      <div className="pt-20">
        <Hero darkMode={darkMode} />
        <HowItWorks darkMode={darkMode} />
        <Features darkMode={darkMode} />
        <Testimonials darkMode={darkMode} />
        <Footer darkMode={darkMode} />
      </div>
    </div>
  );
};

export default Landing;