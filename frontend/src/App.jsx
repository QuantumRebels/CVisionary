import React from "react"
import "./index.css"
import { Routes , Route } from 'react-router-dom'

import Login from './pages/login.jsx'
import Landing from './pages/landing.jsx'
import Dashboard from './pages/dashboard.jsx'
import Resume_builder from "./pages/resume-builder"
import Resume_checker from "./pages/resume-checker"
import Register from "./pages/register"
import Socials from "./pages/socials"
import Social_Github from "./pages/socials-github.jsx"
import Social_Linkedin from "./pages/socials-linkedln.jsx"
import Jobs from "./pages/job.jsx"

function App() {
 

  return (
    <Routes>
        <Route path="/" element = {<Landing/>} />
        <Route path="/login" element = {<Login/>} />
        <Route path="/register" element = {<Register/>} />
        <Route path="/dashboard" element = {<Dashboard/>} />
        <Route path="/resume-builder" element = {<Resume_builder/>} />
        <Route path="/resume-checker" element ={ <Resume_checker/>} />
        <Route path="/socials" element = {<Socials/>} />
        <Route path="/socials/github" element = {<Social_Github/>} />
        <Route path="/socials/linkedin" element = {<Social_Linkedin/>} />
        <Route path="/jobs" element = {<Jobs/>} />

    </Routes>
  )
}

export default App
