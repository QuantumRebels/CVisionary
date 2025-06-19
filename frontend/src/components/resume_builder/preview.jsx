import React, { useState, useEffect } from "react";

const PreviewPanel = ({ currentPrompt }) => {
  const [tab, setTab] = useState("preview");

  return (
    <div className="flex flex-col h-full bg-[#0d0b22] p-6">
      <div className="flex items-center space-x-6 border-b border-gray-700 mb-6">
        <button
          onClick={() => setTab("code")}
          className={`px-3 py-2 text-sm ${
            tab === "code" ? "text-white border-b-2 border-blue-500" : "text-gray-400"
          }`}
        >
          Code
        </button>
        <button
          onClick={() => setTab("preview")}
          className={`px-3 py-2 text-sm ${
            tab === "preview" ? "text-white border-b-2 border-blue-500" : "text-gray-400"
          }`}
        >
          Preview
        </button>
      </div>

      <div className="flex-1 text-center text-white flex flex-col justify-center items-center">
        <h2 className="text-lg font-semibold">Live Preview</h2>
        <p className="text-gray-400 text-sm mt-2">
          Your preview will appear here based on the prompt:
        </p>
        <div className="mt-3 text-blue-400 font-mono text-sm">
          {currentPrompt || "Awaiting your input..."}
        </div>
      </div>
    </div>
  );
};

export default PreviewPanel;
