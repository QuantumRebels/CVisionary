import React from "react";

const testimonials = [
  {
    name: "Alice Johnson",
    text: "ResumeCraft helped me land my dream job at a top tech company. The AI-powered matching feature is a game-changer!",
    img: "https://randomuser.me/api/portraits/women/44.jpg",
  },
  {
    name: "Brian Lee",
    text: "I was struggling to tailor my resume to specific job descriptions until I found ResumeCraft. It's intuitive and effective.",
    img: "https://randomuser.me/api/portraits/men/32.jpg",
  },
  {
    name: "Kristen Smith",
    text: "The ability to export my resume in both PDF and LaTeX formats is incredibly useful. ResumeCraft is a must-have for any job seeker.",
    img: "https://randomuser.me/api/portraits/women/68.jpg",
  },
];

function Testimonials() {
  return (
    <section className="mt-12">
      <h2 className="text-xl font-semibold text-white mb-6 pl-8">Testimonials</h2>
      <div className="flex flex-col md:flex-row gap-6 px-4">
        {testimonials.map((t, idx) => (
          <div
            key={idx}
            className="flex-1 bg-[#18182f] border border-[#23233a] rounded-lg p-6 flex flex-col items-center text-center"
          >
            <img
              src={t.img}
              alt={t.name}
              className="w-16 h-16 rounded-full mb-4 object-cover border-2 border-[#23233a]"
            />
            <p className="text-[#e5e5f7] mb-3">"{t.text}"</p>
            <span className="text-[#b3b3c6] font-semibold">{t.name}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

export default Testimonials;