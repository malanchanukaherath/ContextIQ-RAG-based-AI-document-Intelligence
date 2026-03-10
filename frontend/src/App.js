import React, { useState } from 'react';
import './App.css';
import DocumentUpload from './components/DocumentUpload';
import QueryInterface from './components/QueryInterface';
import Header from './components/Header';
import { FileText, MessageSquare } from 'lucide-react';

function App() {
  const [activeTab, setActiveTab] = useState('query');
  const [uploadedDocs, setUploadedDocs] = useState([]);

  const handleDocumentUploaded = (docName) => {
    setUploadedDocs(prev => [...prev, docName]);
  };

  return (
    <div className="App">
      <Header />
      
      <div className="container">
        <div className="tab-navigation">
          <button 
            className={`tab-button ${activeTab === 'query' ? 'active' : ''}`}
            onClick={() => setActiveTab('query')}
          >
            <MessageSquare size={20} />
            Ask Questions
          </button>
          <button 
            className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
            onClick={() => setActiveTab('upload')}
          >
            <FileText size={20} />
            Upload Documents
          </button>
        </div>

        <div className="content-area">
          {activeTab === 'query' ? (
            <QueryInterface uploadedDocs={uploadedDocs} />
          ) : (
            <DocumentUpload onDocumentUploaded={handleDocumentUploaded} />
          )}
        </div>

        {uploadedDocs.length > 0 && (
          <div className="uploaded-docs-sidebar">
            <h3>📚 Uploaded Documents ({uploadedDocs.length})</h3>
            <ul>
              {uploadedDocs.map((doc, idx) => (
                <li key={idx}>{doc}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
