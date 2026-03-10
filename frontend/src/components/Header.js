import React from 'react';
import './Header.css';
import { Brain } from 'lucide-react';

function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <div className="logo">
          <Brain size={36} />
          <div>
            <h1>RAG Application</h1>
            <p>AI-Powered Document Intelligence</p>
          </div>
        </div>
        <div className="header-info">
          <span className="status-indicator"></span>
          <span>Ready</span>
        </div>
      </div>
    </header>
  );
}

export default Header;
