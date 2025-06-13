import React from "react";
import Navbar from "@/components/landing/Navbar";
import HowItWorks from "@/components/landing/HowItWorks";
import Hero from "@/components/landing/Hero";
import Features from "@/components/landing/Features";
import Testimonials from "@/components/landing/Testimonials";
import Footer from "@/components/landing/Footer";


const Landing = () => {
  return (
    <div className="bg-[#13132a] min-h-screen">
      <Navbar isLoggedIn={false} />
      <div className="pt-20">
        <Hero />
        <HowItWorks />
        <Features />
        <Testimonials />
        <Footer />
        
        {/* Add more sections as needed */}
      </div>
    </div>
  );
};

export default Landing;