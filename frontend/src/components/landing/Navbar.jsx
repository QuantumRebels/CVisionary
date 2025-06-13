import React from "react";
import { Diamond } from "lucide-react";

function Navbar({ isLoggedIn }) {
  return (
    <nav className="bg-[#13132a] px-8 py-4 flex items-center justify-between border-b border-[#23233a]">
      {/* Logo */}
      <div className="flex items-center space-x-2">
        <Diamond className="w-5 h-5 text-white" />
        <span className="font-semibold text-white text-lg">CVisonary</span>
      </div>
      {/* Navigation Buttons */}
      <div className="flex items-center space-x-6">
        {!isLoggedIn ? (
          <>
            <a
              href="#how-it-works"
              className="text-sm font-medium text-white hover:text-blue-400 transition-colors"
            >
              How it works
            </a>
            <a
              href="#reviews"
              className="text-sm font-medium text-white hover:text-blue-400 transition-colors"
            >
              Reviews
            </a>
            <button className="bg-[#23233a] hover:bg-[#35355c] text-white px-5 py-2 rounded-md text-sm font-medium transition-colors">
              Login
            </button>
          </>
        ) : (
          <>
            <a
              href="/dashboard"
              className="text-sm font-medium text-white hover:text-blue-400 transition-colors"
            >
              Dashboard
            </a>
            <a
              href="/builder"
              className="text-sm font-medium text-white hover:text-blue-400 transition-colors"
            >
              Resume Builder
            </a>
            <a
              href="/checker"
              className="text-sm font-medium text-white hover:text-blue-400 transition-colors"
            >
              Resume Checker
            </a>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
