import { Navigate, Route, Routes } from "react-router-dom";
import { Analytics } from "@vercel/analytics/react";

import { AppFooter } from "./components/AppFooter";
import { CountryDetailPage } from "./pages/CountryDetailPage";
import { HomePage } from "./pages/HomePage";
import { RankingsPage } from "./pages/RankingsPage";

function App() {
  return (
    <div className="flex min-h-screen flex-col">
      <div className="flex-1">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/country/:iso3" element={<CountryDetailPage />} />
          <Route path="/rankings" element={<RankingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
      <AppFooter />
      <Analytics />
    </div>
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
