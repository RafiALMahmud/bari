import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import App from "./App";
import Browse from "./pages/Browse";
import PropertyDetail from "./pages/PropertyDetail";
import ListProperty from "./pages/ListProperty";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/browse" element={<Browse />} />
        <Route path="/property/:id" element={<PropertyDetail />} />
        <Route path="/list-property" element={<ListProperty />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
);
