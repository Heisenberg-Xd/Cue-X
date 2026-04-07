import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Visualization from './pages/Visualization';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/visualization/:session_id" element={<Visualization />} />
      </Routes>
    </Router>
  );
}

export default App;
