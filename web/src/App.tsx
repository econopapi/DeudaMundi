import { Navigate, Route, Routes } from "react-router-dom";
import { Analytics } from "@vercel/analytics/react";

import { CountryDetailPage } from "./pages/CountryDetailPage";
import { HomePage } from "./pages/HomePage";
import { RankingsPage } from "./pages/RankingsPage";

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/country/:iso3" element={<CountryDetailPage />} />
        <Route path="/rankings" element={<RankingsPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <Analytics />
    </>
  );
}

export default App;
