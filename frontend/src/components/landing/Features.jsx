import React from "react";
import { CalendarCheck, FileText, Edit3, Download } from "lucide-react";
import { motion } from "framer-motion";

const getFeatures = (darkMode) => [
  {
    icon: <CalendarCheck className={`w-6 h-6 ${darkMode ? "text-white" : "text-blue-700"}`} />,
    title: "AI-Powered Resume",
    description:
      "Automatically generate smart, tailored resumes using advanced AI that adapts to your experience and job goals.",
  },
  {
    icon: <FileText className={`w-6 h-6 ${darkMode ? "text-white" : "text-blue-700"}`} />,
    title: "ATS Friendly",
    description:
      "Optimized formatting ensures your resume passes through Applicant Tracking Systems seamlessly.",
  },
  {
    icon: <Edit3 className={`w-6 h-6 ${darkMode ? "text-white" : "text-blue-700"}`} />,
    title: "Editable Output",
    description:
      "Easily tweak and update your resume with a user-friendly editor—no design skills required.",
  },
  {
    icon: <Download className={`w-6 h-6 ${darkMode ? "text-white" : "text-blue-700"}`} />,
    title: "PDF/LaTeX Export",
    description:
      "Download your resume in high-quality PDF or LaTeX format, ready for print or digital use.",
  },
];

function Features({ darkMode }) {
  const features = getFeatures(darkMode);

  return (
    <section className={`${darkMode ? "bg-[#13132a]" : "bg-white"} py-12 px-6 md:px-12`} id="features">
      <motion.h2
        className={`text-3xl font-bold mb-10 text-center ${darkMode ? "text-white" : "text-gray-900"}`}
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        viewport={{ once: true, amount: 0.3 }}
      >
        Features
      </motion.h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {features.map((feature, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.15 }}
            viewport={{ once: true, amount: 0.2 }}
            className={`rounded-lg px-6 py-6 border shadow-lg transition-all duration-300 hover:scale-[1.03] cursor-default
              ${darkMode
                ? "bg-[#18182f] border-[#23233a] hover:shadow-[0_0_12px_2px_rgba(99,102,241,0.4)] hover:border-indigo-500"
                : "bg-white border-blue-100 hover:shadow-[0_0_12px_2px_rgba(59,130,246,0.15)] hover:border-blue-400"
              }
            `}
          >
            <div className="flex items-center gap-3 mb-3">
              {feature.icon}
              <h3 className={`text-lg font-semibold ${darkMode ? "text-white" : "text-blue-900"}`}>{feature.title}</h3>
            </div>
            <p className={`${darkMode ? "text-[#c0c0dd]" : "text-gray-700"} text-sm leading-relaxed`}>{feature.description}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}

export default Features;
