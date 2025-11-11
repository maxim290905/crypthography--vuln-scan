import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../utils/api';

function ScanDetail() {
  const { id } = useParams();
  const [scan, setScan] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [polling, setPolling] = useState(false);

  useEffect(() => {
    fetchScan();
  }, [id]);

  useEffect(() => {
    if (polling && scan && (scan.status === 'queued' || scan.status === 'running')) {
      const interval = setInterval(() => {
        fetchScan();
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [polling, scan]);

  const fetchScan = async () => {
    try {
      const response = await api.get(`/api/scans/${id}/status`);
      setScan(response.data);
      
      if (response.data.status === 'queued' || response.data.status === 'running') {
        setPolling(true);
      } else if (response.data.status === 'done') {
        setPolling(false);
        fetchResult();
      }
    } catch (err) {
      console.error('Failed to fetch scan:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchResult = async () => {
    try {
      const response = await api.get(`/api/scans/${id}/result`);
      setResult(response.data);
    } catch (err) {
      console.error('Failed to fetch result:', err);
    }
  };

  const downloadPDF = async () => {
    try {
      const response = await api.get(`/api/scans/${id}/report.pdf`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `scan_${id}_report.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Failed to download PDF');
    }
  };

  const downloadJSON = async () => {
    try {
      const response = await api.get(`/api/scans/${id}/result`);
      const dataStr = JSON.stringify(response.data, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = window.URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `scan_${id}_result.json`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Failed to download JSON');
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (!scan) {
    return <div className="container">Scan not found</div>;
  }

  return (
    <div className="container">
      <div style={{ marginBottom: '20px' }}>
        <Link to="/scans" className="btn btn-secondary">← Back to Scans</Link>
      </div>

      <div className="card">
        <h2>Scan Details</h2>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
          <div>
            <strong>Target:</strong> {scan.target || 'N/A'}
          </div>
          <div>
            <strong>Status:</strong>{' '}
            <span className={`status-${scan.status}`}>{scan.status}</span>
          </div>
          <div>
            <strong>Created:</strong>{' '}
            {scan.created_at ? new Date(scan.created_at).toLocaleString() : 'N/A'}
          </div>
          <div>
            <strong>Started:</strong>{' '}
            {scan.started_at ? new Date(scan.started_at).toLocaleString() : 'N/A'}
          </div>
          <div>
            <strong>Finished:</strong>{' '}
            {scan.finished_at ? new Date(scan.finished_at).toLocaleString() : 'N/A'}
          </div>
          {scan.error_message && (
            <div style={{ gridColumn: '1 / -1' }}>
              <strong>Error:</strong>{' '}
              <span style={{ color: '#dc3545' }}>{scan.error_message}</span>
            </div>
          )}
        </div>

        {scan.status === 'done' && result && (
          <>
            <div style={{ marginBottom: '20px' }}>
              <h3>PQ Score: {result.pq_score} ({result.pq_level})</h3>
              <div style={{ marginTop: '10px' }}>
                <button className="btn btn-primary" onClick={downloadPDF} style={{ marginRight: '10px' }}>
                  Download PDF
                </button>
                <button className="btn btn-secondary" onClick={downloadJSON}>
                  Download JSON
                </button>
              </div>
            </div>

            <div className="card" style={{ marginTop: '20px' }}>
              <h3>Summary</h3>
              <p><strong>Total Findings:</strong> {result.summary.total_findings}</p>
              <p><strong>By Severity:</strong></p>
              <ul>
                <li>P0 (Critical): {result.summary.by_severity.P0}</li>
                <li>P1 (High): {result.summary.by_severity.P1}</li>
                <li>P2 (Medium): {result.summary.by_severity.P2}</li>
                <li>P3 (Low): {result.summary.by_severity.P3}</li>
              </ul>
            </div>

            <div className="card" style={{ marginTop: '20px' }}>
              <h3>Findings</h3>
              <table className="table">
                <thead>
                  <tr>
                    <th>Severity</th>
                    <th>Category</th>
                    <th>Asset Type</th>
                    <th>Evidence</th>
                  </tr>
                </thead>
                <tbody>
                  {result.findings.length === 0 ? (
                    <tr>
                      <td colSpan="4" style={{ textAlign: 'center', padding: '40px' }}>
                        No findings
                      </td>
                    </tr>
                  ) : (
                    result.findings.map((finding) => (
                      <tr key={finding.id}>
                        <td>
                          <span className={`badge ${
                            finding.severity === 'P0' ? 'badge-danger' :
                            finding.severity === 'P1' ? 'badge-warning' :
                            finding.severity === 'P2' ? 'badge-info' : 'badge-secondary'
                          }`}>
                            {finding.severity}
                          </span>
                        </td>
                        <td>{finding.category}</td>
                        <td>{finding.asset_type}</td>
                        <td>{finding.evidence || '-'}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </>
        )}

        {(scan.status === 'queued' || scan.status === 'running') && (
          <div className="loading">
            Scan in progress... This page will auto-refresh.
          </div>
        )}
      </div>
    </div>
  );
}

export default ScanDetail;

