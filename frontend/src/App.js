import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import FileUpload from './components/FileUpload';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  return (
  <Router>
    <Routes>
      <Route path="/" element={<FileUpload />} />
      <Route path="/dashboard/:statementId" element={<Dashboard />} />
    </Routes>
</Router>
  );
}

export default App;