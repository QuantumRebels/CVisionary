import React, { useState, useRef } from "react";
import Navbar from "@/components/landing/Navbar";
import { motion } from "framer-motion";
import { FileText, UploadCloud, Search, BarChart2 } from "lucide-react";
import Footer from "../dashboard/footer";

const features = [
  {
    icon: <FileText className="w-6 h-6" />,
    title: "Smart Upload & Analysis",
    desc: "Easily upload your resume in PDF or DOCX format and receive an immediate analysis of its strengths and weaknesses.",
  },
  {
    icon: <Search className="w-6 h-6" />,
    title: "Real-Time Feedback",
    desc: "Get instant, actionable feedback on your resume's content, structure, and formatting to ensure it meets industry standards.",
  },
  {
    icon: <BarChart2 className="w-6 h-6" />,
    title: "Performance Tracking",
    desc: "Track your resume's performance over time, see how it evolves, and measure its impact on your job applications.",
  },
];

const dropVariants = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.7 } },
};

function ResumeReviewer() {
  const [darkMode, setDarkMode] = useState(true);
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const inputRef = useRef();

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") setDragActive(true);
    else if (e.type === "dragleave") setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  return (
    <div className={darkMode ? "bg-[#13132a] min-h-screen" : "bg-white min-h-screen"}>
      <Navbar isLoggedIn={true} darkMode={darkMode} setDarkMode={setDarkMode} />
      <div className="pt-24 px-4 md:px-0 max-w-5xl mx-auto pb-12">
        {/* Upload Section */}
        <motion.section
          initial="initial"
          animate="animate"
          variants={dropVariants}
          className="mb-12"
        >
          <h1 className={`text-3xl md:text-4xl font-bold mb-2 ${darkMode ? "text-white" : "text-gray-900"}`}>
            Upload your resume
          </h1>
          <p className={`mb-8 ${darkMode ? "text-[#b3b3c6]" : "text-gray-700"}`}>
            Get instant feedback and suggestions to improve your resume.
          </p>
          <form
            className={`rounded-xl border-2 border-dashed flex flex-col items-center justify-center transition-all duration-200 relative
              ${dragActive
                ? darkMode
                  ? "border-blue-400 bg-[#18182f]"
                  : "border-blue-400 bg-blue-50"
                : darkMode
                ? "border-[#23233a] bg-[#18182f]"
                : "border-blue-100 bg-white"
              }
              py-12 px-4 mb-6`}
            onDragEnter={handleDrag}
            onSubmit={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
          >
            <UploadCloud className={`w-10 h-10 mb-4 ${darkMode ? "text-blue-400" : "text-blue-600"}`} />
            <span className={`font-semibold text-lg mb-2 ${darkMode ? "text-white" : "text-gray-900"}`}>
              Drag and drop or browse to upload
            </span>
            <span className={`text-sm mb-4 ${darkMode ? "text-[#b3b3c6]" : "text-gray-600"}`}>
              Supported formats: PDF, DOCX
            </span>
            <button
              type="button"
              onClick={() => inputRef.current.click()}
              className={`px-5 py-2 rounded-md font-medium shadow transition-all
                ${darkMode
                  ? "bg-[#23233a] hover:bg-[#35355c] text-white"
                  : "bg-blue-100 hover:bg-blue-200 text-blue-700 border border-blue-200"
                }
              `}
            >
              Browse Files
            </button>
            <input
              ref={inputRef}
              type="file"
              accept=".pdf,.doc,.docx"
              className="hidden"
              onChange={handleChange}
            />
            {file && (
              <div className={`mt-4 text-sm ${darkMode ? "text-blue-300" : "text-blue-700"}`}>
                Selected: <span className="font-semibold">{file.name}</span>
              </div>
            )}
            {dragActive && (
              <div className="absolute inset-0 rounded-xl border-4 border-blue-400 border-dashed pointer-events-none" />
            )}
          </form>
          <div className="flex justify-end">
            <button
              className={`px-6 py-2 rounded-md font-semibold transition-all
                ${darkMode
                  ? "bg-blue-600 hover:bg-blue-700 text-white"
                  : "bg-blue-600 hover:bg-blue-700 text-white"
                }
              `}
              disabled={!file}
            >
              Analyze Resume
            </button>
          </div>
        </motion.section>

        {/* Features Section */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.2 }}
        >
          <h2 className={`text-2xl font-bold mb-6 ${darkMode ? "text-white" : "text-gray-900"}`}>
            Features
          </h2>
          <h3 className={`text-2xl md:text-3xl font-extrabold mb-2 ${darkMode ? "text-white" : "text-gray-900"}`}>
            Enhance Your Resume with Powerful Features
          </h3>
          <p className={`mb-8 ${darkMode ? "text-[#b3b3c6]" : "text-gray-700"}`}>
            Our platform offers a suite of tools designed to help you create a standout resume. From instant feedback to detailed analytics, we’ve got you covered.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {features.map((f, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: i * 0.15 }}
                viewport={{ once: true, amount: 0.2 }}
                className={`rounded-lg px-6 py-6 border shadow-lg transition-all duration-300 hover:scale-[1.03] cursor-default
                  ${darkMode
                    ? "bg-[#18182f] border-[#23233a] hover:shadow-[0_0_12px_2px_rgba(99,102,241,0.4)] hover:border-indigo-500"
                    : "bg-white border-blue-100 hover:shadow-[0_0_12px_2px_rgba(59,130,246,0.15)] hover:border-blue-400"
                  }
                `}
              >
                <div className={`flex items-center gap-3 mb-3 ${darkMode ? "text-blue-300" : "text-blue-700"}`}>
                  {f.icon}
                  <h4 className={`text-lg font-semibold ${darkMode ? "text-white" : "text-blue-900"}`}>{f.title}</h4>
                </div>
                <p className={`${darkMode ? "text-[#c0c0dd]" : "text-gray-700"} text-sm leading-relaxed`}>{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </motion.section>
      </div>
      <Footer />
    </div>
  );
}

export default ResumeReviewer;