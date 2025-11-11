import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Projects from './components/Projects';
import Scans from './components/Scans';
import ScanDetail from './components/ScanDetail';
import CreateScan from './components/CreateScan';
import { getToken, removeToken } from './utils/auth';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!getToken());

  useEffect(() => {
    setIsAuthenticated(!!getToken());
  }, []);

  const handleLogout = () => {
    removeToken();
    setIsAuthenticated(false);
  };

  return (
    <Router>
      <div className="App">
        {isAuthenticated && (
          <div className="header">
            <div className="nav">
              <h1>Cryptography Vulnerability Scanner</h1>
              <div className="nav-links">
                <Link to="/dashboard">Dashboard</Link>
                <Link to="/projects">Projects</Link>
                <Link to="/scans">Scans</Link>
                <button className="btn btn-secondary" onClick={handleLogout}>
                  Logout
                </button>
              </div>
            </div>
          </div>
        )}
        
        <Routes>
          <Route
            path="/login"
            element={
              isAuthenticated ? <Navigate to="/dashboard" /> : <Login onLogin={() => setIsAuthenticated(true)} />
            }
          />
          <Route
            path="/dashboard"
            element={
              isAuthenticated ? <Dashboard /> : <Navigate to="/login" />
            }
          />
          <Route
            path="/projects"
            element={
              isAuthenticated ? <Projects /> : <Navigate to="/login" />
            }
          />
          <Route
            path="/scans"
            element={
              isAuthenticated ? <Scans /> : <Navigate to="/login" />
            }
          />
          <Route
            path="/scans/create"
            element={
              isAuthenticated ? <CreateScan /> : <Navigate to="/login" />
            }
          />
          <Route
            path="/scans/:id"
            element={
              isAuthenticated ? <ScanDetail /> : <Navigate to="/login" />
            }
          />
          <Route
            path="/"
            element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} />}
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

