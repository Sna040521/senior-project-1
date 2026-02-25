import { BrowserRouter, Routes, Route } from "react-router-dom";

import Layout from "./components/Layout.jsx";
import CreateSession from "./pages/CreateSession.jsx";
import UploadData from "./pages/UploadData.jsx";
import Recommendations from "./pages/Recommendations.jsx";
import GraduationAudit from "./pages/GraduationAudit.jsx";
import AdminCourses from "./pages/AdminCourses.jsx";
function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<CreateSession />} />
          <Route path="/upload" element={<UploadData />} />
          <Route path="/recommendations" element={<Recommendations />} />
          <Route path="/graduation-audit" element={<GraduationAudit />} />
          <Route path="/admin/courses" element={<AdminCourses />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;