// ✅ Enhanced Hero, Navbar, HowItWorks, and Testimonials Sections
import React from "react";
import { Sparkles, Moon, Sun } from "lucide-react";
import Logo from "../../assets/images/logo.jpg";
import { motion } from "framer-motion";


function Navbar({ isLoggedIn }) {
  const [darkMode, setDarkMode] = React.useState(true);

  return (
    <nav className="w-full bg-[#13132a] px-8 py-4 flex items-center justify-between border-b border-[#23233a] fixed top-0 left-0 z-50">
      <div className="flex items-center space-x-2">
        <Sparkles className="w-5 h-5 text-white" />
        <span className="font-semibold text-white text-lg">CVisionary</span>
      </div>
      <div className="flex items-center space-x-6">
        <button onClick={() => setDarkMode(!darkMode)} className="text-white hover:text-yellow-400">
          {darkMode ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        {!isLoggedIn ? (
          <>
            <a href="#how-it-works" className="text-sm font-medium text-white hover:text-blue-400 transition-colors">
              How it works
            </a>
            <a href="#testimonials" className="text-sm font-medium text-white hover:text-blue-400 transition-colors">
              Reviews
            </a>
            <a href="/login">
              <button className="bg-[#23233a] hover:bg-[#35355c] text-white px-5 py-2 rounded-md text-sm font-medium transition-colors">
                Login
              </button>
            </a>
          </>
        ) : (
          <>
            <a href="/dashboard" className="text-sm font-medium text-white hover:text-blue-400 transition-colors">
              Dashboard
            </a>
            <a href="/builder" className="text-sm font-medium text-white hover:text-blue-400 transition-colors">
              Resume Builder
            </a>
            <a href="/checker" className="text-sm font-medium text-white hover:text-blue-400 transition-colors">
              Resume Checker
            </a>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;