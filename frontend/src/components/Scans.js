import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../utils/api';

function Scans() {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState('');

  useEffect(() => {
    fetchProjects();
    fetchScans();
  }, [selectedProject]);

  const fetchProjects = async () => {
    try {
      const response = await api.get('/api/projects');
      setProjects(response.data);
    } catch (err) {
      console.error('Failed to fetch projects:', err);
    }
  };

  const fetchScans = async () => {
    try {
      const url = selectedProject
        ? `/api/scans?project_id=${selectedProject}`
        : '/api/scans';
      const response = await api.get(url);
      setScans(response.data);
    } catch (err) {
      console.error('Failed to fetch scans:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Scans</h2>
        <Link to="/scans/create" className="btn btn-primary">Create Scan</Link>
      </div>

      <div className="card" style={{ marginBottom: '20px' }}>
        <div className="form-group">
          <label>Filter by Project</label>
          <select
            value={selectedProject}
            onChange={(e) => setSelectedProject(e.target.value)}
          >
            <option value="">All Projects</option>
            {projects.map((project) => (
              <option key={project.id} value={project.id}>
                {project.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Target</th>
              <th>Status</th>
              <th>PQ Score</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {scans.length === 0 ? (
              <tr>
                <td colSpan="6" style={{ textAlign: 'center', padding: '40px' }}>
                  No scans yet. <Link to="/scans/create">Create your first scan</Link>
                </td>
              </tr>
            ) : (
              scans.map((scan) => (
                <tr key={scan.id}>
                  <td>{scan.id}</td>
                  <td>{scan.target}</td>
                  <td>
                    <span className={`status-${scan.status}`}>
                      {scan.status}
                    </span>
                  </td>
                  <td>
                    {scan.pq_score !== null ? (
                      <span className={`badge ${
                        scan.pq_score >= 86 ? 'badge-danger' :
                        scan.pq_score >= 61 ? 'badge-warning' :
                        scan.pq_score >= 31 ? 'badge-info' : 'badge-success'
                      }`}>
                        {scan.pq_score}
                      </span>
                    ) : (
                      '-'
                    )}
                  </td>
                  <td>{new Date(scan.created_at).toLocaleString()}</td>
                  <td>
                    <Link to={`/scans/${scan.id}`} className="btn btn-primary" style={{ padding: '5px 10px', fontSize: '12px' }}>
                      View
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Scans;

