import { Navigate, Route, Routes } from "react-router-dom";

import { CountryDetailPage } from "./pages/CountryDetailPage";
import { HomePage } from "./pages/HomePage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/country/:iso3" element={<CountryDetailPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
