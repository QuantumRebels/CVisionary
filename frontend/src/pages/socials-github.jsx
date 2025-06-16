import React from "react";
import Navbar from "@/components/landing/Navbar";
import { useState } from "react";
import { getInitialDarkMode, setDarkModePreference } from "@/utils/theme";
import Social_Github from "../components/socials/socials-github";
import Footer from "@/components/dashboard/footer";

const Social_Github_Connect = () => {
  const [darkMode, setDarkMode] = useState(getInitialDarkMode());

  const handleSetDarkMode = (value) => {
    setDarkMode(value);
    setDarkModePreference(value);
  };

  return (
    <div className={`app ${darkMode ? "dark" : "light"}`}>
      <Navbar isLoggedIn={true} darkMode={darkMode} setDarkMode={handleSetDarkMode} />
      <Social_Github darkMode={darkMode} />
      <Footer darkMode={darkMode} />
    </div>
  );
};

export default Social_Github_Connect;