import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LeadList from './components/LeadList';
import LeadDetail from './components/LeadDetail';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<LeadList />} />
          <Route path="/lead/:id" element={<LeadDetail />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;