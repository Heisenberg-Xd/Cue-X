import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Home from './pages/Home';
import UploadPage from './pages/UploadPage';
import Analytics from './pages/Analytics';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/"                          element={<Home />} />
        <Route path="/upload"                    element={<UploadPage />} />
        <Route path="/visualization/:session_id" element={<Analytics />} />
        
        {/* Dashboard Route */}
        <Route path="/dashboard/:session_id" element={<Analytics />} />
        
        {/* Fallback for missing routes */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
