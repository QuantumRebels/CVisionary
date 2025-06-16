import React, { useState } from "react";
import Navbar from "@/components/landing/Navbar";
import QuickActions from "@/components/dashboard/actions";
import WelcomeSection from "@/components/dashboard/welcome";
import ResumeGallery from "@/components/dashboard/resume";
import JobApplications from "@/components/dashboard/jobs";
import Footer from "@/components/dashboard/footer";
import { getInitialDarkMode, setDarkModePreference } from "@/utils/theme";

const Dashboard = () => {
  const [darkMode, setDarkMode] = useState(getInitialDarkMode());

  const handleSetDarkMode = (value) => {
    setDarkMode(value);
    setDarkModePreference(value);
  };

  return (
    <div className={`app ${darkMode ? "dark" : "light"}`}>
      <Navbar isLoggedIn={true} darkMode={darkMode} setDarkMode={handleSetDarkMode} />
      <WelcomeSection darkMode={darkMode} />
      <QuickActions darkMode={darkMode} />
      <ResumeGallery darkMode={darkMode} />
      <JobApplications darkMode={darkMode} />
      <Footer darkMode={darkMode} />
    </div>
  );
};

export default Dashboard;