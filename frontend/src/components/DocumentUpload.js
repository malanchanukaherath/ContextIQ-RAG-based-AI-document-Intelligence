import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './DocumentUpload.css';
import { Upload, CheckCircle, AlertCircle, Loader, Trash2, RefreshCw } from 'lucide-react';

function DocumentUpload({ onDocumentUploaded }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [loadingDocs, setLoadingDocs] = useState(false);
  const [deletingDoc, setDeletingDoc] = useState(null);

  // Fetch documents on component mount
  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    setLoadingDocs(true);
    try {
      const response = await axios.get('/api/documents');
      setDocuments(response.data.documents || []);
    } catch (error) {
      console.error('Error fetching documents:', error);
    } finally {
      setLoadingDocs(false);
    }
  };

  const handleDeleteDocument = async (filename) => {
    if (!window.confirm(`Are you sure you want to delete "${filename}"? This will remove all associated data.`)) {
      return;
    }

    setDeletingDoc(filename);
    try {
      await axios.delete(`/api/documents/${encodeURIComponent(filename)}`);
      setStatus({ 
        type: 'success', 
        message: `Successfully deleted ${filename}` 
      });
      await fetchDocuments();
    } catch (error) {
      setStatus({ 
        type: 'error', 
        message: error.response?.data?.detail || `Failed to delete ${filename}` 
      });
    } finally {
      setDeletingDoc(null);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setStatus(null);
    } else {
      setStatus({ type: 'error', message: 'Please select a PDF file' });
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setStatus(null);
    } else {
      setStatus({ type: 'error', message: 'Please drop a PDF file' });
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setStatus(null);

    try {
      // Create FormData to upload the file
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      // Upload the file to the backend
      const response = await axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setStatus({ 
        type: 'success', 
        message: `Successfully uploaded ${selectedFile.name}! Processing in background...` 
      });
      onDocumentUploaded(selectedFile.name);
      setSelectedFile(null);
      // Refresh document list after upload
      await fetchDocuments();
    } catch (error) {
      setStatus({ 
        type: 'error', 
        message: error.response?.data?.detail || 'Failed to upload document' 
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="document-upload">
      <h2>Upload PDF Documents</h2>
      <p className="subtitle">Upload your documents to enable AI-powered search and Q&A</p>

      <div 
        className={`upload-zone ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <Upload size={48} />
        <h3>Drag & Drop your PDF here</h3>
        <p>or</p>
        <label htmlFor="file-input" className="file-input-label">
          Browse Files
        </label>
        <input
          id="file-input"
          type="file"
          accept=".pdf"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
      </div>

      {selectedFile && (
        <div className="selected-file">
          <div className="file-info">
            <CheckCircle size={20} color="#28a745" />
            <span>{selectedFile.name}</span>
            <span className="file-size">
              ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
            </span>
          </div>
          <button 
            className="upload-button"
            onClick={handleUpload}
            disabled={uploading}
          >
            {uploading ? (
              <>
                <Loader className="spinner" size={20} />
                Processing...
              </>
            ) : (
              'Upload & Process'
            )}
          </button>
        </div>
      )}

      {status && (
        <div className={`status-message ${status.type}`}>
          {status.type === 'success' ? (
            <CheckCircle size={20} />
          ) : (
            <AlertCircle size={20} />
          )}
          <span>{status.message}</span>
        </div>
      )}

      <div className="info-section">
        <h3>How it works:</h3>
        <ol>
          <li>Upload your PDF documents</li>
          <li>Documents are automatically chunked and embedded</li>
          <li>Ask questions in the Query tab</li>
          <li>Get AI-powered answers based on your documents</li>
        </ol>
      </div>

      <div className="documents-section">
        <div className="documents-header">
          <h3>Uploaded Documents ({documents.length})</h3>
          <button 
            className="refresh-button" 
            onClick={fetchDocuments}
            disabled={loadingDocs}
            title="Refresh document list"
          >
            <RefreshCw size={16} className={loadingDocs ? 'spinning' : ''} />
          </button>
        </div>
        
        {loadingDocs ? (
          <div className="loading-documents">
            <Loader className="spinner" size={20} />
            <span>Loading documents...</span>
          </div>
        ) : documents.length === 0 ? (
          <p className="no-documents">No documents uploaded yet</p>
        ) : (
          <ul className="documents-list">
            {documents.map((doc) => (
              <li key={doc} className="document-item">
                <div className="document-info">
                  <CheckCircle size={16} color="#28a745" />
                  <span className="document-name">{doc}</span>
                </div>
                <button
                  className="delete-button"
                  onClick={() => handleDeleteDocument(doc)}
                  disabled={deletingDoc === doc}
                  title="Delete document"
                >
                  {deletingDoc === doc ? (
                    <Loader className="spinner" size={16} />
                  ) : (
                    <Trash2 size={16} />
                  )}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default DocumentUpload;
