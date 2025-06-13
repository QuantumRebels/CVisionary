import React from "react";
import { CalendarCheck, FileText, Edit3, Download } from "lucide-react";

function Features() {
  return (
    <section className="bg-[#13132a] py-8 px-4">
      <h2 className="text-xl font-semibold text-white mb-4">Features</h2>
      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1 border border-[#23233a] rounded-lg px-6 py-5 flex items-center gap-3 bg-[#18182f]">
          <CalendarCheck className="w-6 h-6 text-white" />
          <span className="text-white font-medium">AI-Powered Resume</span>
        </div>
        <div className="flex-1 border border-[#23233a] rounded-lg px-6 py-5 flex items-center gap-3 bg-[#18182f]">
          <FileText className="w-6 h-6 text-white" />
          <span className="text-white font-medium">ATS Friendly</span>
        </div>
        <div className="flex-1 border border-[#23233a] rounded-lg px-6 py-5 flex items-center gap-3 bg-[#18182f]">
          <Edit3 className="w-6 h-6 text-white" />
          <span className="text-white font-medium">Editable Output</span>
        </div>
        <div className="flex-1 border border-[#23233a] rounded-lg px-6 py-5 flex items-center gap-3 bg-[#18182f]">
          <Download className="w-6 h-6 text-white" />
          <span className="text-white font-medium">PDF/LaTeX Export</span>
        </div>
      </div>
    </section>
  );
}

export default Features;