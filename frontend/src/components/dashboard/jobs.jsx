import React from "react";
import { FaBriefcase, FaInfoCircle } from "react-icons/fa";

const jobs = [
  {
    title: "Frontend Engineer - Google",
    status: "Under Review",
    color: "bg-[#29244a]",
  },
  {
    title: "React Developer - Netflix",
    status: "Interview Scheduled",
    color: "bg-[#3a2f4d]",
  },
  {
    title: "UI Designer - Amazon",
    status: "Awaiting Response",
    color: "bg-[#2b254d]",
  },
  {
    title: "Full Stack Developer - Microsoft",
    status: "Under Review",
    color: "bg-[#33284f]",
  },
  {
    title: "DevOps Engineer - IBM",
    status: "Selected",
    color: "bg-[#2d244d]",
  },
  {
    title: "Data Analyst - Adobe",
    status: "Rejected",
    color: "bg-[#36294a]",
  },
];

const JobApplications = ({ darkMode }) => {
  return (
    <section className={`${darkMode ? "bg-[#0d0b22] text-white" : "bg-white text-[#18181b]"} px-6 md:px-10 py-14`}>
      <h2 className={`text-2xl font-bold mb-8 ml-20 ${darkMode ? "text-white" : "text-[#18181b]"}`}>Job Applications</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-10 max-w-7xl mx-auto">
        {jobs.map((job, idx) => (
          <div
            key={idx}
            className={`rounded-2xl p-6 border shadow-[0_0_10px_rgba(59,130,246,0.3)] transition-all duration-300 transform hover:scale-105
              ${darkMode
                ? `${job.color} border-gray-700`
                : "bg-gray-100 border-gray-200"
              }
            `}
          >
            <div className="flex items-center gap-2 text-lg font-semibold mb-2">
              <FaBriefcase className="text-blue-400" />
              {job.title}
            </div>
            <div className={`flex items-center gap-2 text-sm ${darkMode ? "text-gray-300" : "text-gray-600"}`}>
              <FaInfoCircle className="text-green-400" />
              Status: {job.status}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

export default JobApplications;