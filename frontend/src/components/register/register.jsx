// src/pages/Register.jsx
import RegisterImage from "../../assets/images/login.jpg"
import React from "react";

const Register = () => {
  return (
    <div className="min-h-screen bg-[#0f0f1c] flex items-center justify-center px-4">
      <div className="bg-[#1a1a2e] text-white rounded-2xl shadow-lg flex flex-col md:flex-row overflow-hidden w-full max-w-4xl">
        {/* Right Branding/Image Section */}
        <div className="hidden md:flex items-center justify-center bg-[#202030] w-full md:w-1/2">
          <img
            src={RegisterImage} // Replace with your brand logo
            alt="CVisionary Logo"
            className="object-cover w-full h-full max-w-md max-h-md rounded-r-2xl"
          />
        </div>
        {/* Left Section (Form) */}
        <div className="flex-1 p-10">
          <h2 className="text-3xl font-bold mb-2">Create an Account</h2>
          <p className="text-gray-400 mb-6">Join the CVisionary platform</p>

          <form className="space-y-5">
            <div>
              <label className="block mb-1 text-sm font-medium">Full Name</label>
              <input
                type="text"
                placeholder="John Doe"
                className="w-full px-4 py-2 bg-[#2a2a40] border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block mb-1 text-sm font-medium">Email</label>
              <input
                type="email"
                placeholder="you@example.com"
                className="w-full px-4 py-2 bg-[#2a2a40] border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block mb-1 text-sm font-medium">Password</label>
              <input
                type="password"
                placeholder="••••••••"
                className="w-full px-4 py-2 bg-[#2a2a40] border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 transition duration-300 py-2 rounded-md font-semibold"
            >
              Sign Up
            </button>
          </form>

          <div className="my-6 flex items-center gap-2 text-gray-500 text-sm">
            <hr className="flex-1 border-gray-700" />
            OR
            <hr className="flex-1 border-gray-700" />
          </div>

          <div className="flex gap-4">
            <button className="flex-1 bg-white text-black py-2 rounded-md hover:opacity-90 transition duration-300 font-medium">
              Sign Up with Google
            </button>
            <button className="flex-1 bg-gray-900 text-white py-2 rounded-md hover:bg-gray-800 transition duration-300 font-medium">
              Sign Up with GitHub
            </button>
          </div>

          <p className="text-center text-sm text-gray-400 mt-6">
            Already have an account?{" "}
            <a href="/login" className="text-blue-400 hover:underline">
              Login
            </a>
          </p>
        </div>

        
      </div>
    </div>
  );
};

export default Register;
