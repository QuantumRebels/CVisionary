import React from "react";

function Footer() {
  return (
    <footer className="mt-16 py-8 px-4 bg-[#13132a] text-[#b3b3c6]">
      <div className="flex flex-col items-center max-w-5xl mx-auto w-full gap-2">
        <div className="flex gap-12 text-sm mb-2">
          <a href="#" className="hover:underline">How it Works</a>
          <a href="#" className="hover:underline">Generate Resumes</a>
          <a href="#" className="hover:underline">Privacy Policy</a>
        </div>
        <div className="text-xs text-center">
          © 2025 CVisionary. All rights reserved.
        </div>
      </div>
    </footer>
  );
}

export default Footer;