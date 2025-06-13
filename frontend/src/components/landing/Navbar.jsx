import React from "react";
import { Diamond } from "lucide-react";

function Navbar({ isLoggedIn }) {
  return (
    <nav className="bg-[#0D0D1F] px-6 py-4 flex items-center justify-between border-b border-[#1E1E2F] text-white">
      <div className="flex items-center space-x-2">
        <Diamond className="w-4 h-4 text-white" />
        <span className="font-semibold text-white">CVisionary</span>
      </div>
      <div className="flex items-center space-x-6">
        {!isLoggedIn ? (
          <>
            <a
              href="#how-it-works"
              className="text-sm font-medium hover:text-blue-400 transition-colors"
            >
              How it Works
            </a>
            <a
              href="#reviews"
              className="text-sm font-medium hover:text-blue-400 transition-colors"
            >
              Reviews
            </a>
            <button className="bg-[#2D2D44] hover:bg-[#3B3B5C] text-white py-2 px-4 rounded-md text-sm font-medium transition-colors">
              Login
            </button>
          </>
        ) : (
          <>
            <a
              href="/dashboard"
              className="text-sm font-medium hover:text-blue-400 transition-colors"
            >
              Dashboard
            </a>
            <a
              href="/builder"
              className="text-sm font-medium hover:text-blue-400 transition-colors"
            >
              Resume Builder
            </a>
            <a
              href="/checker"
              className="text-sm font-medium hover:text-blue-400 transition-colors"
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
