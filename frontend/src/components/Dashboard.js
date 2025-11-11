import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../utils/api';

function Dashboard() {
  const [stats, setStats] = useState({
    totalScans: 0,
    activeScans: 0,
    completedScans: 0,
    totalProjects: 0,
  });
  const [recentScans, setRecentScans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [scansResponse, projectsResponse] = await Promise.all([
        api.get('/api/scans'),
        api.get('/api/projects'),
      ]);

      const scans = scansResponse.data;
      const projects = projectsResponse.data;

      setStats({
        totalScans: scans.length,
        activeScans: scans.filter(s => s.status === 'running' || s.status === 'queued').length,
        completedScans: scans.filter(s => s.status === 'done').length,
        totalProjects: projects.length,
      });

      setRecentScans(scans.slice(0, 5));
    } catch (err) {
      console.error('Failed to fetch data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="container">
      <h2>Dashboard</h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '30px' }}>
        <div className="card">
          <h3>Total Scans</h3>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#0066cc' }}>{stats.totalScans}</p>
        </div>
        <div className="card">
          <h3>Active Scans</h3>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#17a2b8' }}>{stats.activeScans}</p>
        </div>
        <div className="card">
          <h3>Completed</h3>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#28a745' }}>{stats.completedScans}</p>
        </div>
        <div className="card">
          <h3>Projects</h3>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#6c757d' }}>{stats.totalProjects}</p>
        </div>
      </div>

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h3>Recent Scans</h3>
          <Link to="/scans/create" className="btn btn-primary">Create Scan</Link>
        </div>
        <table className="table">
          <thead>
            <tr>
              <th>Target</th>
              <th>Status</th>
              <th>PQ Score</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {recentScans.length === 0 ? (
              <tr>
                <td colSpan="5" style={{ textAlign: 'center', padding: '40px' }}>
                  No scans yet. <Link to="/scans/create">Create your first scan</Link>
                </td>
              </tr>
            ) : (
              recentScans.map((scan) => (
                <tr key={scan.id}>
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

export default Dashboard;

