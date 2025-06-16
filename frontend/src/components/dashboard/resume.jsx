import React from "react";
import ResumeImage from "../../assets/images/resume.jpeg";

const resumes = [
  {
    name: "Resume For Frontend Developer",
    image: ResumeImage,
    border: "border-purple-500",
    textColor: "text-purple-400",
  },
  {
    name: "Resume For Backend Developer",
    image: ResumeImage,
    border: "border-green-500",
    textColor: "text-green-400",
  },
  {
    name: "Resume For Full Stack Developer",
    image: ResumeImage,
    border: "border-yellow-400",
    textColor: "text-yellow-400",
  },
  {
    name: "Tech Friendly Resume",
    image: ResumeImage,
    border: "border-pink-500",
    textColor: "text-pink-400",
  },
];

const ResumeGallery = ({ darkMode }) => {
  return (
    <section className={`${darkMode ? "bg-[#0d0b22] text-white" : "bg-white text-[#18181b]"} px-6 md:px-10 py-14`}>
      <h2 className={`text-2xl font-bold mb-6 ml-20 ${darkMode ? "text-white" : "text-[#18181b]"}`}>Past Resumes</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-10 max-w-7xl mx-auto mt-12">
        {resumes.map((resume, idx) => (
          <div
            key={idx}
            className={`rounded-2xl p-4 transition-all duration-300 transform hover:scale-105
              ${darkMode
                ? "bg-[#15132b] shadow-[0_0_15px_rgba(59,130,246,0.4)] border border-gray-600"
                : "bg-gray-100 shadow-[0_0_15px_rgba(59,130,246,0.08)] border border-gray-200"
              }
            `}
          >
            <img
              src={resume.image}
              alt={resume.name}
              className={`rounded-xl mb-4 w-full object-cover h-96 border ${darkMode ? "border-gray-600" : "border-gray-200"}`}
            />
            <div className={`font-semibold text-md mb-1 ${resume.textColor}`}>{resume.name}</div>
          </div>
        ))}
      </div>
    </section>
  );
};
export default ResumeGallery;