import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';

function CreateScan() {
  const [projects, setProjects] = useState([]);
  const [target, setTarget] = useState('');
  const [projectId, setProjectId] = useState('');
  const [scanType, setScanType] = useState('tls_network');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await api.get('/api/projects');
      setProjects(response.data);
      if (response.data.length > 0) {
        setProjectId(response.data[0].id.toString());
      }
    } catch (err) {
      console.error('Failed to fetch projects:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await api.post('/api/scans', {
        target,
        project_id: parseInt(projectId),
        scan_type: scanType,
        notes: notes || null,
      });

      navigate(`/scans/${response.data.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create scan');
    } finally {
      setLoading(false);
    }
  };

  if (projects.length === 0) {
    return (
      <div className="container">
        <div className="alert alert-error">
          You need to create a project first. <a href="/projects">Go to Projects</a>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <h2>Create Scan</h2>
      <div className="card">
        {error && <div className="alert alert-error">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Target (Domain or IP)</label>
            <input
              type="text"
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              placeholder="example.com or 192.168.1.1"
              required
            />
          </div>
          <div className="form-group">
            <label>Project</label>
            <select
              value={projectId}
              onChange={(e) => setProjectId(e.target.value)}
              required
            >
              {projects.map((project) => (
                <option key={project.id} value={project.id}>
                  {project.name}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Scan Type</label>
            <select
              value={scanType}
              onChange={(e) => setScanType(e.target.value)}
            >
              <option value="tls_network">TLS & Network</option>
            </select>
          </div>
          <div className="form-group">
            <label>Notes (Optional)</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Additional notes about this scan..."
            />
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Creating...' : 'Create Scan'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default CreateScan;


