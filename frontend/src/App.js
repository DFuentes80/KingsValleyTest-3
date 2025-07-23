import React from "react";
import "./App.css";  
import { BrowserRouter, Routes, Route } from "react-router-dom";
import GameContainer from "./components/GameContainer";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<GameContainer />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
