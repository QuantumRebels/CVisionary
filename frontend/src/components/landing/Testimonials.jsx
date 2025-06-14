import React from "react";
import { motion } from "framer-motion";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useState } from "react";

const testimonials = [
  {
    name: "Ananya Sharma",
    text: "ResumeCraft helped me personalize my resume perfectly for MNC roles. I got interview calls within days!",
    img: "https://randomuser.me/api/portraits/women/21.jpg",
  },
  {
    name: "Rajiv Menon",
    text: "I love the LaTeX export feature. It gave my resume a polished and professional look that stood out.",
    img: "https://randomuser.me/api/portraits/men/45.jpg",
  },
  {
    name: "Priya Mehta",
    text: "The scraping and JD matching saved me hours! Highly recommended to anyone job hunting.",
    img: "https://randomuser.me/api/portraits/women/11.jpg",
  },
  {
    name: "Amitabh Rao",
    text: "Simple to use and super powerful. The AI suggestions really made my resume pop!",
    img: "https://randomuser.me/api/portraits/men/22.jpg",
  },
  {
    name: "Sneha Nair",
    text: "Perfect for freshers and professionals alike. Got selected for 3 interviews within a week!",
    img: "https://randomuser.me/api/portraits/women/65.jpg",
  },
  {
    name: "Rohit Verma",
    text: "ResumeCraft made it so easy to align my resume with job requirements. Great tool!",
    img: "https://randomuser.me/api/portraits/men/28.jpg",
  },
  {
    name: "Meera Iyer",
    text: "I’m from a non-tech background and ResumeCraft still helped me stand out. Love it!",
    img: "https://randomuser.me/api/portraits/women/78.jpg",
  },
  {
    name: "Karthik Reddy",
    text: "The platform is fast, clean and actually useful. Would recommend to anyone serious about job hunting.",
    img: "https://randomuser.me/api/portraits/men/56.jpg",
  },
  {
    name: "Divya Kulkarni",
    text: "Easy-to-use UI and powerful AI. It’s like having a career coach in your pocket!",
    img: "https://randomuser.me/api/portraits/women/29.jpg",
  },
];

function Testimonials() {
  const [startIndex, setStartIndex] = useState(0);
  const visibleTestimonials = testimonials.slice(startIndex, startIndex + 3);

  const handlePrev = () => {
    setStartIndex((prev) => (prev - 3 + testimonials.length) % testimonials.length);
  };

  const handleNext = () => {
    setStartIndex((prev) => (prev + 3) % testimonials.length);
  };

  return (
    <section className="mt-16 px-4 md:px-12" id="testimonials">
      <motion.h2
        className="text-3xl font-bold text-white mb-2 text-center"
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        viewport={{ once: true }}
      >
        Testimonials
      </motion.h2>
      <p className="text-[#c7c7de] text-center mb-8 max-w-2xl mx-auto">
        Hear from real users across India who’ve landed opportunities faster and more confidently with ResumeCraft.
      </p>

      <div className="relative">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {visibleTestimonials.map((t, idx) => (
            <motion.div
              key={idx}
              className="bg-[#18182f] border border-[#23233a] rounded-xl p-6 flex flex-col items-center text-center transition-all 
                         hover:shadow-[0_0_20px_2px_rgba(99,102,241,0.4)] hover:scale-[1.03]"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: idx * 0.2 }}
              viewport={{ once: true }}
            >
              <img
                src={t.img}
                alt={t.name}
                className="w-20 h-20 rounded-full mb-4 object-cover border-2 border-indigo-500"
              />
              <p className="text-[#dcdcf0] mb-4 text-sm leading-relaxed">"{t.text}"</p>
              <span className="text-[#b3b3c6] font-semibold">{t.name}</span>
            </motion.div>
          ))}
        </div>

        {/* Arrows */}
        <div className="absolute top-1/2 left-0 transform -translate-y-1/2 z-10">
          <button onClick={handlePrev} className="bg-[#1f1f3a] hover:bg-[#2a2a4d] text-white p-2 rounded-full shadow-md">
            <ChevronLeft />
          </button>
        </div>
        <div className="absolute top-1/2 right-0 transform -translate-y-1/2 z-10">
          <button onClick={handleNext} className="bg-[#1f1f3a] hover:bg-[#2a2a4d] text-white p-2 rounded-full shadow-md">
            <ChevronRight />
          </button>
        </div>
      </div>
    </section>
  );
}

export default Testimonials;
