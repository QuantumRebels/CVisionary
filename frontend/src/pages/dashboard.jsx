import { React}  from "react";
import Navbar from "@/components/landing/Navbar";
import QuickActions from "@/components/dashboard/actions";
import WelcomeSection from "@/components/dashboard/welcome";
import ResumeGallery from "@/components/dashboard/resume";
import JobApplications from "@/components/dashboard/jobs";
import Footer from "@/components/dashboard/footer";

const dashboard  = () => {
  return (
    <div className="app">
       <Navbar isLoggedIn={true} darkMode={true} setDarkMode={() => {}} />
        <WelcomeSection/>
        <QuickActions />
        <ResumeGallery />
        <JobApplications />
        <Footer/>
    </div>
  );
}

export default dashboard ;