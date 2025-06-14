import LoginImage from "../../assets/images/login.jpg";
import React from "react";
import { useNavigate } from "react-router-dom";
import auth, { githubProvider, googleProvider, signInWithPopup } from "../../firebase";

const Login = () => {
  const navigate = useNavigate();

  const handleGoogleLogin = async () => {
    try {
      const result = await signInWithPopup(auth, googleProvider);
      console.log("Google login successful: ", result.user);
      // ✅ Save name to localStorage
      localStorage.setItem("userName", result.user.displayName);
      navigate("/dashboard");
    } catch (error) {
      console.error("Google login error: ", error.message);
    }
  };

  const handleGithubSignUp = async () => {
    try {
      const result = await signInWithPopup(auth, githubProvider);
      console.log("GitHub login successful: ", result.user);
      // ✅ Save name to localStorage
      localStorage.setItem("userName", result.user.displayName);
      navigate("/dashboard");
    } catch (error) {
      if (error.code === "auth/account-exists-with-different-credential") {
        alert("An account already exists with a different login method (like Google). Please use that to log in.");
      } else {
        console.error("GitHub login error:", error.message);
        alert("GitHub login failed. Please try again.");
      }
    }
  }; // ←✅ This closing brace was missing in your original code

  return (
    <div className="min-h-screen bg-[#0f0f1c] flex items-center justify-center px-4">
      <div className="bg-[#1a1a2e] text-white rounded-2xl shadow-lg flex flex-col md:flex-row overflow-hidden w-full max-w-4xl">
        {/* Left Section */}
        <div className="flex-1 p-10">
          <h2 className="text-3xl font-bold mb-2">Welcome Back</h2>
          <p className="text-gray-400 mb-6">Login to your CVisionary account</p>

          <form className="space-y-5">
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
              <div className="text-right mt-1">
                <a href="#" className="text-sm text-blue-400 hover:underline">
                  Forgot password?
                </a>
              </div>
            </div>
            <button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 transition duration-300 py-2 rounded-md font-semibold"
            >
              Login
            </button>
          </form>

          <div className="my-6 flex items-center gap-2 text-gray-500 text-sm">
            <hr className="flex-1 border-gray-700" />
            OR
            <hr className="flex-1 border-gray-700" />
          </div>

          <div className="flex gap-4">
            <button
              onClick={handleGithubSignUp}
              className="flex-1 bg-white text-black py-2 rounded-md hover:opacity-90 transition duration-300 font-medium"
            >
              Login with GitHub
            </button>
            <button
              onClick={handleGoogleLogin}
              className="flex-1 bg-blue-700 text-white py-2 rounded-md hover:bg-blue-800 transition duration-300 font-medium"
            >
              Login with Google
            </button>
          </div>

          <p className="text-center text-sm text-gray-400 mt-6">
            Don't have an account?{" "}
            <a href="/register" className="text-blue-400 hover:underline">
              Sign up
            </a>
          </p>
        </div>

        {/* Right Image Section */}
        <div className="hidden md:flex items-center justify-center bg-[#202030] w-full md:w-1/2">
          <img
            src={LoginImage}
            alt="CVisionary Logo"
            className="object-cover w-full h-full max-w-md max-h-md rounded-r-2xl"
          />
        </div>
      </div>
    </div>
  );
};

export default Login;
