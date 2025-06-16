import React, { useRef, useState } from "react";
import { Dialog } from "@headlessui/react";
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";

const LinkedInUpload = () => {
  const [file, setFile] = useState(null);
  const [isOpen, setIsOpen] = useState(false);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();
  const [userName, setUserName] = useState("");

  useEffect(() => {
    const storedName = localStorage.getItem("userName");
    if (storedName) setUserName(storedName);
  }, []);

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected && selected.type === "application/pdf") {
      setFile(selected);
    } else {
      alert("Please upload a valid LinkedIn PDF.");
    }
  };

  const handleAnalyze = () => {
    if (!file) {
      alert("Please upload your LinkedIn PDF first.");
      return;
    }

    // Simulate backend processing
    console.log("Analyzing LinkedIn profile:", file.name);
    setIsOpen(true);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0a0a23] text-white px-4">
      {/* Go to Dashboard Button */}
      <div className="absolute top-24 right-6">
        <button
          onClick={() => navigate("/dashboard")}
          className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg"
        >
          Go to Dashboard
        </button>
      </div>
      <div className="w-full max-w-3xl mx-auto">
        <h1 className="text-2xl md:text-3xl font-bold mb-2 text-start leading-tight ">
          Hello  {userName && `, ${userName}`}  !! Upload Your LinkedIn PDF
        </h1>
        <p className="mb-6 text-gray-400">Upload your LinkedIn PDF to extract your experience, education, and achievements.</p>

        <div className="border-2 border-dashed border-gray-600 rounded-xl p-10 text-center hover:border-blue-500 transition-all duration-300">
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            className="hidden"
            ref={fileInputRef}
          />
          <div className="text-4xl mb-2">📄</div>
          <p className="text-lg font-semibold">
            {file ? `Uploaded: ${file.name}` : "Drag and drop or browse to upload"}
          </p>
          <p className="text-sm text-gray-400">Supported format: PDF</p>
          <button
            onClick={() => fileInputRef.current.click()}
            className="mt-4 px-5 py-2 bg-[#1e1e40] text-white font-medium rounded-lg hover:bg-[#2a2a5c] transition"
          >
            Browse Files
          </button>
        </div>

        <div className="mt-6 text-right">
          <button
            onClick={handleAnalyze}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg"
          >
            Analyze LinkedIn Scrap
          </button>
        </div>
      </div>

      {/* Modal for Extracted Data */}
      <Dialog open={isOpen} onClose={() => setIsOpen(false)} className="relative z-50">
        <div className="fixed inset-0 bg-black/60" aria-hidden="true" />
        <div className="fixed inset-0 flex items-center justify-center p-4 overflow-y-auto">
          <Dialog.Panel className="bg-[#1E1B3A] text-white p-6 rounded-xl w-full max-w-2xl shadow-xl">
            <Dialog.Title className="text-2xl font-bold mb-4">
              LinkedIn Insights
            </Dialog.Title>

            <div className="space-y-4">
              <div>
                <p className="font-semibold text-blue-400 mb-1">Bio:</p>
                <p>
                  Enthusiastic Full Stack Developer with 2+ years of experience in building scalable web apps and a strong presence in open-source contributions.
                </p>
              </div>

              <div>
                <p className="font-semibold text-blue-400 mb-1">Experience:</p>
                <ul className="list-disc ml-6 space-y-1">
                  <li>Software Developer Intern @ ABC Corp (Jan 2024 - Jun 2024)</li>
                  <li>Open Source Contributor @ GirlScript Summer of Code</li>
                </ul>
              </div>

              <div>
                <p className="font-semibold text-blue-400 mb-1">Education:</p>
                <ul className="list-disc ml-6 space-y-1">
                  <li>B.Tech in Computer Science, IIIT Bhubaneswar (2022–2026)</li>
                </ul>
              </div>

              <div>
                <p className="font-semibold text-blue-400 mb-1">Achievements:</p>
                <ul className="list-disc ml-6 space-y-1">
                  <li>Winner – HackThisFall 2024</li>
                  <li>Top 5 finalist – Smart India Hackathon 2023</li>
                </ul>
              </div>
            </div>

            <button
              onClick={() => setIsOpen(false)}
              className="mt-6 bg-blue-600 hover:bg-blue-700 w-full py-3 rounded-xl text-white font-semibold transition-transform transform hover:scale-105"
            >
              Close
            </button>
          </Dialog.Panel>
        </div>
      </Dialog>
    </div>
  );
};

export default LinkedInUpload;
