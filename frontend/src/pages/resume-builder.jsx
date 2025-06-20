// App.jsx
import { useState } from "react";
import Welcome from "../components/resume_builder/welcome";
import ChatWindow from "../components/resume_builder/chatwindow";
import LivePreview from "../components/resume_builder/preview";
import { AnimatePresence, motion } from "framer-motion";
import Navbar from "@/components/landing/Navbar";
import { getInitialDarkMode, setDarkModePreference } from "@/utils/theme";

export default function Resume_builder() {
  const [hasPrompted, setHasPrompted] = useState(false);
  const [prompt, setPrompt] = useState("");

  const handleInitialPrompt = (text) => {
    setPrompt(text);
    setHasPrompted(true);
  };


  const [darkMode, setDarkMode] = useState(getInitialDarkMode());

  const handleSetDarkMode = (value) => {
    setDarkMode(value);
    setDarkModePreference(value);
  };
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Navbar isLoggedIn={true} darkMode={darkMode} setDarkMode={handleSetDarkMode} />
      <AnimatePresence>
        {!hasPrompted ? (
          <Welcome onPromptSubmit={handleInitialPrompt} />
        ) : (
          <motion.div
            className="flex h-screen"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="w-1/2 border-r border-gray-700">
              <ChatWindow initialPrompt={prompt} />
            </div>
            <div className="w-1/2">
              <LivePreview prompt={prompt} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}