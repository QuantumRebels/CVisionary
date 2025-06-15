import React, { useState } from "react";
import ResumeReviewer from "@/components/resume_checker/ResumeReviewer";
import { getInitialDarkMode, setDarkModePreference } from "@/utils/theme";

const ResumeChecker = () => {
  const [darkMode, setDarkMode] = useState(getInitialDarkMode());

  const handleSetDarkMode = (value) => {
    setDarkMode(value);
    setDarkModePreference(value);
  };

  return <ResumeReviewer darkMode={darkMode} setDarkMode={handleSetDarkMode} />;
};

export default ResumeChecker;