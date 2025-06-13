import React from "react";
import Navbar from "@/components/landing/Navbar";
import Hero from "@/components/landing/Hero";
import Features from "@/components/landing/Features";

const Landing = () => {
  return (
    <div className="bg-[#13132a] min-h-screen">
      <Navbar isLoggedIn={false} />
      <div className="pt-20"> {/* Add top padding to prevent overlap */}
        <Hero />
        <Features />
        {/* Add more sections as needed */}
      </div>
    </div>
  );
};

export default Landing;