import { React}  from "react";
import Navbar from "@/components/landing/Navbar";

const dashboard  = () => {
  return (
    <div className="app">
       <Navbar isLoggedIn={true} darkMode={true} setDarkMode={() => {}} />
    </div>
  );
}

export default dashboard ;