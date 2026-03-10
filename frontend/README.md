# RAG Application - Frontend

A modern React-based UI for the RAG (Retrieval-Augmented Generation) application.

## Features

- **Document Upload**: Drag & drop or browse to upload PDF documents
- **AI-Powered Q&A**: Ask questions and get intelligent answers from your documents
- **Modern UI**: Beautiful, responsive design with smooth animations
- **Real-time Status**: Track document processing and query status
- **Document Management**: View all uploaded documents in sidebar

## Getting Started

### Prerequisites

- Node.js 16+ 
- Backend server running on `http://localhost:8000`

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm start
```

Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

### Build for Production

```bash
npm run build
```

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Header.js           # App header with logo
│   │   ├── Header.css
│   │   ├── DocumentUpload.js   # PDF upload component
│   │   ├── DocumentUpload.css
│   │   ├── QueryInterface.js   # Q&A chat interface
│   │   └── QueryInterface.css
│   ├── App.js                  # Main app component
│   ├── App.css
│   ├── index.js
│   └── index.css
└── package.json
```

## Usage

1. **Upload Documents**: 
   - Switch to "Upload Documents" tab
   - Drag & drop a PDF or click "Browse Files"
   - Click "Upload & Process"

2. **Ask Questions**:
   - Switch to "Ask Questions" tab
   - Type your question in the input field
   - Press Enter or click Send
   - View AI-generated answers with sources

## Configuration

The frontend proxies API requests to `http://localhost:8000` by default. To change this, update the `proxy` field in `package.json`.

## Technologies Used

- React 18
- Axios for API calls
- Lucide React for icons
- CSS3 with modern features
