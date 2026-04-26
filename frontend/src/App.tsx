import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthPage } from './pages/AuthPage';
import UploadPage from './pages/UploadPage';
import Analytics from './pages/Analytics';
import { RequireAuth } from './components/RequireAuth';

function App() {
  return (
    <Router>
      <Routes>
        {/* Root → Auth */}
        <Route path="/" element={<Navigate to="/auth" replace />} />

        {/* Auth (public) */}
        <Route path="/auth" element={<AuthPage />} />

        {/* Workspace = Upload page (protected) */}
        <Route
          path="/workspace"
          element={
            <RequireAuth>
              <UploadPage />
            </RequireAuth>
          }
        />

        {/* Upload (protected) */}
        <Route
          path="/upload"
          element={
            <RequireAuth>
              <UploadPage />
            </RequireAuth>
          }
        />

        {/* Analytics dashboard (protected) */}
        <Route
          path="/dashboard/:dataset_id"
          element={
            <RequireAuth>
              <Analytics />
            </RequireAuth>
          }
        />

        {/* Catch-all → auth */}
        <Route path="*" element={<Navigate to="/auth" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
