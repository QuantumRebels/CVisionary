import React, { useEffect, useState } from "react";
import { Dialog } from "@headlessui/react";
import { useNavigate } from "react-router-dom";

const JobApply = ({ darkMode }) => {
  const [welcomeName, setWelcomeName] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();

  const [userName, setUserName] = useState("");

  useEffect(() => {
    const storedName = localStorage.getItem("userName");
    if (storedName) setUserName(storedName);
  }, []);

  // Form states
  const [jobTitle, setJobTitle] = useState("");
  const [jobDesc, setJobDesc] = useState("");
  const [company, setCompany] = useState("");
  const [location, setLocation] = useState("");
  const [category, setCategory] = useState("");
  const [jobType, setJobType] = useState("");
  const [stipend, setStipend] = useState("");

  useEffect(() => {
    const user = JSON.parse(localStorage.getItem("user"));
    if (user?.name) {
      setWelcomeName(user.name);
    } else {
      setWelcomeName("Developer");
    }
  }, []);

  const isFormValid = () => {
    return (
      jobTitle.trim() &&
      jobDesc.trim() &&
      company.trim() &&
      location.trim() &&
      category.trim() &&
      jobType.trim() &&
      stipend.trim()
    );
  };

  // Theme classes
  const bgClass = darkMode ? "bg-[#0a0a23]" : "bg-white";
  const textClass = darkMode ? "text-white" : "text-gray-900";
  const subTextClass = darkMode ? "text-gray-400" : "text-gray-600";
  const btnBg = darkMode
    ? "bg-blue-600 hover:bg-blue-700 text-white"
    : "bg-blue-500 hover:bg-blue-600 text-white";
  const btnShadow = darkMode
    ? "shadow-[0_0_15px_rgba(59,130,246,0.4)]"
    : "shadow-[0_0_15px_rgba(30,41,59,0.25)]";
  const modalBg = darkMode ? "bg-[#1E1B3A] text-white" : "bg-blue-50 text-gray-900";
  const inputBg = darkMode ? "bg-[#2a2752] text-white" : "bg-blue-100 text-gray-900";
  const cancelBtn = darkMode
    ? "bg-gray-600 hover:bg-gray-700 text-white"
    : "bg-gray-200 hover:bg-gray-300 text-gray-900";

  return (
    <div className={`min-h-screen ${bgClass} ${textClass} flex flex-col items-center justify-center px-4 transition-colors duration-300`}>
      {/* Go to Dashboard Button */}
      <div className="absolute top-24 right-6">
        <button
          onClick={() => navigate("/dashboard")}
          className={`${btnBg} font-semibold py-2 px-6 rounded-lg transition-colors duration-300`}
        >
          Go to Dashboard
        </button>
      </div>

      <div className="text-center mb-10">
        {/* Welcome Heading */}
        <h1 className="text-4xl md:text-5xl font-bold mb-2 text-center leading-tight">
          Hey {userName && `, ${userName}`}
        </h1>
        <p className={`${subTextClass} mt-6 text-lg`}>Generate Your Resumes as per your Jobs</p>
      </div>

      <button
        onClick={() => setIsOpen(true)}
        className={`${btnBg} font-semibold py-3 px-8 rounded-xl ${btnShadow} transform hover:scale-105 transition`}
      >
        Apply For Your Job
      </button>

      {/* Modal */}
      <Dialog open={isOpen} onClose={() => setIsOpen(false)} className="relative z-50">
        <div className="fixed inset-0 bg-black/60" aria-hidden="true" />
        <div className="fixed inset-0 flex items-center justify-center p-4 overflow-y-auto">
          <Dialog.Panel className={`${modalBg} p-6 rounded-xl w-full max-w-2xl shadow-xl`}>
            <Dialog.Title className="text-2xl font-bold mb-4">
              Job Application Form
            </Dialog.Title>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input
                type="text"
                placeholder="Job Title"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                className={`p-3 rounded-lg ${inputBg} focus:outline-none`}
              />
              <input
                type="text"
                placeholder="Company Name"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                className={`p-3 rounded-lg ${inputBg} focus:outline-none`}
              />
              <input
                type="text"
                placeholder="Location"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className={`p-3 rounded-lg ${inputBg} focus:outline-none`}
              />
              <input
                type="text"
                placeholder="Category"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className={`p-3 rounded-lg ${inputBg} focus:outline-none`}
              />
              <input
                type="text"
                placeholder="Job Type (e.g. Full-time)"
                value={jobType}
                onChange={(e) => setJobType(e.target.value)}
                className={`p-3 rounded-lg ${inputBg} focus:outline-none`}
              />
              <input
                type="text"
                placeholder="Stipend"
                value={stipend}
                onChange={(e) => setStipend(e.target.value)}
                className={`p-3 rounded-lg ${inputBg} focus:outline-none`}
              />
              <textarea
                placeholder="Job Description"
                value={jobDesc}
                onChange={(e) => setJobDesc(e.target.value)}
                rows={4}
                className={`p-3 rounded-lg ${inputBg} focus:outline-none md:col-span-2`}
              />
            </div>

            <div className="mt-6 flex justify-between">
              <button
                onClick={() => setIsOpen(false)}
                className={`${cancelBtn} py-2 px-6 rounded-lg`}
              >
                Cancel
              </button>

              <button
                onClick={() => navigate("/resume-builder")}
                disabled={!isFormValid()}
                className={`${
                  isFormValid()
                    ? `${btnBg} cursor-pointer`
                    : "bg-blue-800 opacity-50 cursor-not-allowed"
                } text-white font-semibold py-3 px-8 rounded-xl ${btnShadow} transition`}
              >
                Generate Resume Now
              </button>
            </div>
          </Dialog.Panel>
        </div>
      </Dialog>
    </div>
  );
};

export default JobApply;
