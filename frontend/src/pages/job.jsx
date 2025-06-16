import React from "react";
import Navbar from "@/components/landing/Navbar";
import { useState } from "react";
import { getInitialDarkMode, setDarkModePreference } from "@/utils/theme";
import JobApply from "@/components/job/job";
import Footer from "@/components/dashboard/footer";

const Socials = () => {
  const [darkMode, setDarkMode] = useState(getInitialDarkMode());

  const handleSetDarkMode = (value) => {
    setDarkMode(value);
    setDarkModePreference(value);
  };

  return (
    <div className={`app ${darkMode ? "dark" : "light"}`}>
      <Navbar isLoggedIn={true} darkMode={darkMode} setDarkMode={handleSetDarkMode} />
      <JobApply darkMode={darkMode} />
      <Footer darkMode={darkMode} />
    </div>
  );
};

export default Socials;