import React from "react";
import { Sparkles, Moon, Sun } from "lucide-react";
import { motion } from "framer-motion";
import { getAuth, signOut } from "firebase/auth";

function Navbar({ isLoggedIn, darkMode, setDarkMode, }) {
  
  const handlelogout = async () => {
    try {
      const auth = getAuth();

      await signOut(auth);
      console.log("User logged out successfully");
      window.location.href = "/"; // Redirect to home page after logout


    }
    catch (error) {
      console.log("Error is logging out : ", error.message);
    }
  }
  return (
    <nav
      className={`w-full px-8 py-4 flex items-center justify-between border-b fixed top-0 left-0 z-50
        ${darkMode ? "bg-[#13132a] border-[#23233a]" : "bg-white border-gray-200"}
      `}
    >
      <div className="flex items-center space-x-2">
        <Sparkles className={darkMode ? "w-5 h-5 text-white" : "w-5 h-5 text-blue-600"} />
        <span className={`font-semibold text-lg ${darkMode ? "text-white" : "text-gray-900"}`}>CVisionary</span>
      </div>
      <div className="flex items-center space-x-6">
        <button
          onClick={() => setDarkMode(!darkMode)}
          className={darkMode
            ? "text-white hover:text-yellow-400"
            : "text-gray-700 hover:text-yellow-500"
          }
        >
          {darkMode ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        {!isLoggedIn ? (
          <>
            <a
              href="#how-it-works"
              className={`text-sm font-medium transition-colors ${darkMode ? "text-white hover:text-blue-400" : "text-gray-800 hover:text-blue-600"}`}
            >
              How it works
            </a>
            <a
              href="#testimonials"
              className={`text-sm font-medium transition-colors ${darkMode ? "text-white hover:text-blue-400" : "text-gray-800 hover:text-blue-600"}`}
            >
              Reviews
            </a>
           
            <a href="/login">
              <button
                className={darkMode
                  ? "bg-[#23233a] hover:bg-[#35355c] text-white px-5 py-2 rounded-md text-sm font-medium transition-colors"
                  : "bg-gray-100 hover:bg-blue-100 text-blue-700 px-5 py-2 rounded-md text-sm font-medium transition-colors border border-blue-200"
                }
              >
                Login
              </button>
            </a>
          </>
        ) : (
          <>
            <a href="/dashboard" className={darkMode ? "text-sm font-medium text-white hover:text-blue-400" : "text-sm font-medium text-gray-800 hover:text-blue-600"}>
              Dashboard
            </a>
            <a href="/builder" className={darkMode ? "text-sm font-medium text-white hover:text-blue-400" : "text-sm font-medium text-gray-800 hover:text-blue-600"}>
              Resume Builder
            </a>
            <a href="/resume-checker" className={darkMode ? "text-sm font-medium text-white hover:text-blue-400" : "text-sm font-medium text-gray-800 hover:text-blue-600"}>
              Resume Checker
            </a>
            <button
              onClick={handlelogout}
              className={
                darkMode
                  ? "bg-[#23233a] hover:bg-[#35355c] text-white px-5 py-2 rounded-md text-sm font-medium transition-colors"
                  : "bg-gray-100 hover:bg-red-100 text-red-600 px-5 py-2 rounded-md text-sm font-medium transition-colors border border-red-300"
              }
            >
              Logout
            </button>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;