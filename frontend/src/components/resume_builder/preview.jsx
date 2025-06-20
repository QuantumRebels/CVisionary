import React, { useState } from "react";

const PreviewPanel = ({ prompt, darkMode }) => {
  const [tab, setTab] = useState("preview");

  const bgClass = darkMode ? "bg-[#0d0b22]" : "bg-white";
  const textClass = darkMode ? "text-white" : "text-gray-900";
  const borderClass = darkMode ? "border-gray-700" : "border-blue-200";
  const subTextClass = darkMode ? "text-gray-400" : "text-gray-600";
  const tabActive = darkMode
    ? "text-white border-b-2 border-blue-500"
    : "text-blue-700 border-b-2 border-blue-500";
  const tabInactive = darkMode ? "text-gray-400" : "text-gray-500";

  return (
    <div className={`flex flex-col h-full ${bgClass} p-6 ${textClass} transition-colors duration-300`}>
      <div className={`flex items-center space-x-6 border-b mb-6 ${borderClass}`}>
        <button
          onClick={() => setTab("code")}
          className={`px-3 py-2 text-sm ${tab === "code" ? tabActive : tabInactive}`}
        >
          Code
        </button>
        <button
          onClick={() => setTab("preview")}
          className={`px-3 py-2 text-sm ${tab === "preview" ? tabActive : tabInactive}`}
        >
          Preview
        </button>
      </div>

      <div className={`flex-1 text-center flex flex-col justify-center items-center ${textClass}`}>
        <h2 className="text-lg font-semibold">Live Preview</h2>
        <p className={`text-sm mt-2 ${subTextClass}`}>
          Your preview will appear here based on the prompt:
        </p>
        <div className="mt-3 font-mono text-sm text-blue-400">
          {prompt || "Awaiting your input..."}
        </div>
      </div>
    </div>
  );
};

export default PreviewPanel;
