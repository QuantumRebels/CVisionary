import React from "react";

function Footer({ darkMode }) {
  return (
    <footer className={`mt-16 py-8 px-4 ${darkMode ? "bg-[#13132a] text-[#b3b3c6]" : "bg-white text-blue-700"}`}>
      <div className="flex flex-col items-center max-w-5xl mx-auto w-full gap-2">
        <div className="flex gap-12 text-sm mb-2">
          <a href="#" className={darkMode ? "hover:underline" : "hover:underline text-blue-700"}>How it Works</a>
          <a href="#" className={darkMode ? "hover:underline" : "hover:underline text-blue-700"}>Generate Resumes</a>
          <a href="#" className={darkMode ? "hover:underline" : "hover:underline text-blue-700"}>Privacy Policy</a>
        </div>
        <div className="text-xs text-center">
          © 2025 CVisionary. All rights reserved.
        </div>
      </div>
    </footer>
  );
}

export default Footer;