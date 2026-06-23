import React from "react";
import { createRoot } from "react-dom/client";
import PDLCConfigurator from "./PDLCConfigurator.jsx";

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <PDLCConfigurator />
  </React.StrictMode>
);
