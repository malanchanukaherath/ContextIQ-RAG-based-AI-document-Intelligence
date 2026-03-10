import React, { useState } from 'react';
import axios from 'axios';
import './QueryInterface.css';
import { Send, Loader, BookOpen, Sparkles } from 'lucide-react';

function QueryInterface({ uploadedDocs }) {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim() || loading) return;

    const currentQuestion = question;
    setQuestion('');
    setLoading(true);

    // Add user question to history
    setHistory(prev => [...prev, { type: 'question', content: currentQuestion }]);

    try {
      const response = await axios.post('/api/query', null, {
        params: {
          question: currentQuestion,
          top_k: 5
        }
      });

      // Add answer to history
      setHistory(prev => [...prev, { 
        type: 'answer', 
        content: response.data.answer || 'No answer received',
        sources: response.data.sources,
        numContexts: response.data.num_contexts
      }]);
    } catch (error) {
      setHistory(prev => [...prev, { 
        type: 'error', 
        content: error.response?.data?.detail || 'Failed to get answer. Please try again.' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (exampleQuestion) => {
    setQuestion(exampleQuestion);
  };

  const exampleQuestions = [
    "What are the main topics discussed in the documents?",
    "Can you summarize the key points?",
    "What recommendations are mentioned?",
    "Are there any specific dates or deadlines mentioned?"
  ];

  return (
    <div className="query-interface">
      <div className="query-header">
        <h2>
          <Sparkles size={24} />
          Ask Questions About Your Documents
        </h2>
        <p>Get instant AI-powered answers based on your uploaded PDFs</p>
      </div>

      {uploadedDocs.length === 0 ? (
        <div className="empty-state">
          <BookOpen size={64} />
          <h3>No documents uploaded yet</h3>
          <p>Upload PDF documents first to start asking questions</p>
        </div>
      ) : (
        <>
          <div className="chat-container">
            {history.length === 0 ? (
              <div className="welcome-message">
                <h3>👋 Welcome!</h3>
                <p>Try asking a question about your documents, or use one of these examples:</p>
                <div className="example-questions">
                  {exampleQuestions.map((example, idx) => (
                    <button
                      key={idx}
                      className="example-button"
                      onClick={() => handleExampleClick(example)}
                    >
                      {example}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="chat-history">
                {history.map((item, idx) => (
                  <div key={idx} className={`chat-message ${item.type}`}>
                    {item.type === 'question' && (
                      <div className="message-content question-content">
                        <div className="message-icon">🤔</div>
                        <div className="message-text">{item.content}</div>
                      </div>
                    )}
                    {item.type === 'answer' && (
                      <div className="message-content answer-content">
                        <div className="message-icon">🤖</div>
                        <div className="message-text">
                          <div className="answer-text">{item.content}</div>
                          {item.sources && item.sources.length > 0 && (
                            <div className="sources">
                              <strong>📚 Sources:</strong>
                              <ul>
                                {item.sources.map((source, i) => (
                                  <li key={i}>{source}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {item.numContexts && (
                            <div className="context-info">
                              Used {item.numContexts} context{item.numContexts !== 1 ? 's' : ''} from documents
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                    {item.type === 'error' && (
                      <div className="message-content error-content">
                        <div className="message-icon">⚠️</div>
                        <div className="message-text">{item.content}</div>
                      </div>
                    )}
                  </div>
                ))}
                {loading && (
                  <div className="chat-message loading">
                    <div className="message-content answer-content">
                      <div className="message-icon">🤖</div>
                      <div className="message-text">
                        <Loader className="spinner" size={20} />
                        Thinking...
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          <form className="query-form" onSubmit={handleSubmit}>
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask a question about your documents..."
              disabled={loading}
            />
            <button type="submit" disabled={loading || !question.trim()}>
              {loading ? (
                <Loader className="spinner" size={20} />
              ) : (
                <Send size={20} />
              )}
            </button>
          </form>
        </>
      )}
    </div>
  );
}

export default QueryInterface;
