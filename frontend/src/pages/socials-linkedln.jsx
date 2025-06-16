import React from "react";
import Navbar from "@/components/landing/Navbar";
import { useState } from "react";
import { getInitialDarkMode, setDarkModePreference } from "@/utils/theme";
import Social_Linkedln from "../components/socials/socials-linikedln"
import Footer from "@/components/dashboard/footer";

const Social_Linkedin_Connect= () => {

  const [darkMode, setDarkMode] = useState(getInitialDarkMode());

  const handleSetDarkMode = (value) => {
    setDarkMode(value);
    setDarkModePreference(value);
  };

  return (
    <div className={`app ${darkMode ? "dark" : "light"}`}>
      <Navbar isLoggedIn={true}  darkMode={darkMode} setDarkMode={handleSetDarkMode}/>

      <Social_Linkedln darkMode={darkMode} />
     <Footer darkMode={darkMode} />

    </div>
  )
}

export default Social_Linkedin_Connect;