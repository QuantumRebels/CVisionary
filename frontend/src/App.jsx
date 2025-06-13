import React from "react"
import { Routes , Route } from 'react-router-dom'

import Login from './pages/login.jsx'
import Landing from './pages/landing.jsx'
import Dashboard from './pages/dashboard.jsx'
import Resume_builder from "./pages/resume-builder"
import Resume_checker from "./pages/resume-checker"
import Register from "./pages/register"

function App() {
 

  return (
    <Routes>
        <Route path="/" element = {<Landing/>} />
        <Route path="/login" element = {<Login/>} />
        <Route path="/register" element = {<Register/>} />
        <Route path="/dashboard" element = {<Dashboard/>} />
        <Route path="/resume_builder" element = {<Resume_builder/>} />
        <Route path="/resume_checker" element ={ <Resume_checker/>} />

    </Routes>
  )
}

export default App
