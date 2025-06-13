import React from "react";

const ResumeIllustration = () => (
  <svg
    width="320"
    height="240"
    viewBox="0 0 320 240"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className="rounded-lg bg-[#e9d6c3]"
    style={{ background: "#e9d6c3" }}
  >
    <rect x="0" y="0" width="320" height="240" rx="12" fill="#e9d6c3" />
    {/* Hand */}
    <path
      d="M70 180 Q90 170 100 200 Q110 230 130 210 Q150 190 140 170 Q130 150 120 160 Q110 170 100 150 Q90 130 80 150 Q70 170 70 180 Z"
      fill="#e2b48c"
    />
    {/* Resume Paper */}
    <rect x="110" y="50" width="100" height="120" rx="4" fill="#fff" />
    {/* Headshot */}
    <circle cx="160" cy="75" r="16" fill="#f3d6b6" />
    <ellipse cx="160" cy="80" rx="10" ry="6" fill="#b48a78" />
    {/* Resume lines */}
    <rect x="125" y="100" width="70" height="6" rx="2" fill="#ececec" />
    <rect x="125" y="112" width="70" height="4" rx="2" fill="#ececec" />
    <rect x="125" y="122" width="70" height="4" rx="2" fill="#ececec" />
    <rect x="125" y="132" width="50" height="4" rx="2" fill="#ececec" />
    <rect x="125" y="142" width="40" height="4" rx="2" fill="#ececec" />
    {/* "RESUME" text */}
    <text x="135" y="95" fontSize="10" fill="#888" fontFamily="sans-serif" fontWeight="bold">
      RESUME
    </text>
  </svg>
);

export default ResumeIllustration;