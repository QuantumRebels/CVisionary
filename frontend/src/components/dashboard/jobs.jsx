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

const JobApplications = () => {
  return (
    <section className="bg-[#0d0b22] text-white px-6 md:px-10 py-14">
      <h2 className="text-2xl font-bold mb-8 ml-4 ml-20">Job Applications</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-10 max-w-7xl mx-auto">
        {jobs.map((job, idx) => (
          <div
            key={idx}
            className={`rounded-2xl ${job.color} p-6 border border-gray-700 shadow-[0_0_10px_rgba(59,130,246,0.3)] transition-all duration-300 transform hover:scale-105`}
          >
            <div className="flex items-center gap-2 text-lg font-semibold mb-2">
              <FaBriefcase className="text-blue-400" />
              {job.title}
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-300">
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
