// import React from "react"


// function App() {
 

//   return (
//     <>
//       <div className="app">
//           <h1 className="text-red-600 text-6xl font-bold">Welcome to CVisionary</h1>
//           <p className="text-3xl text-black font-semibold mt-4">We are currently under construction</p>
//       </div>
     
//     </>
//   )
// }

// export default App

import React from "react";
import Navbar from "./Navbar";
import Hero from "./hero";
import Features from "./features";

function Landing() {
  const isLoggedIn = false;

  return (
    <>
      <Navbar isLoggedIn={isLoggedIn} />
      <Hero />
      {/* Hero*/}
      <Features />
      {/* ...rest of your landing page... */}
    </>
  );
}

export default Landing;

