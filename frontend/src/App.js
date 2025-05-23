import React, { useState } from 'react';
import './App.css';

function App() {
  const [topic, setTopic] = useState("");
  const [tone, setTone] = useState("formal");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [pptBlob, setPptBlob] = useState(null);
  const [progress, setProgress] = useState(0);

  // Simulate progress for better UX
  const simulateProgress = () => {
    setProgress(0);
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90) {
          clearInterval(interval);
          return 90;
        }
        return prev + Math.random() * 15;
      });
    }, 200);
    return interval;
  };

  const handleGenerate = async () => {
    setLoading(true);
    setError("");
    setPptBlob(null);

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/generate-ppt/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic, tone }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText);
      }

      const blob = await response.blob();
      setPptBlob(blob);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadPPT = () => {
    if (pptBlob) {
      const url = URL.createObjectURL(pptBlob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${topic || "presentation"}.pptx`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  const exampleTopics = [
    "Climate Change Solutions",
    "Introduction to AI",
    "Digital Marketing Strategy",
    "Remote Work Best Practices",
    "Sustainable Business Models"
  ];

  return (
    <div className="app-container">
      <div className="app-wrapper">
        {/* Main Card */}
        <div className="main-card">
          {/* Animated background elements */}
          <div className="bg-element bg-element-1"></div>
          <div className="bg-element bg-element-2"></div>
          
          {/* Header */}
          <div className="header">
            <div className="icon-container">
              <span className="icon">🎨</span>
            </div>
            <h1 className="title">AI PowerPoint Generator</h1>
            <p className="subtitle">Create stunning presentations in seconds</p>
          </div>

          {/* Topic Input */}
          <div className="form-group">
            <label className="form-label">
              📝 What's your presentation about?
            </label>
            <div className="input-container">
              <input
                type="text"
                className="form-input"
                placeholder="Enter your topic..."
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
              />
              {topic && (
                <div className="input-check">✓</div>
              )}
            </div>
            
            {/* Topic Suggestions */}
            {!topic && (
              <div className="suggestions">
                <p className="suggestions-label">💡 Try these examples:</p>
                <div className="suggestions-list">
                  {exampleTopics.slice(0, 3).map((example, idx) => (
                    <button
                      key={idx}
                      onClick={() => setTopic(example)}
                      className="suggestion-btn"
                    >
                      {example}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Tone Selection */}
          <div className="form-group">
            <label className="form-label">
              🎭 Choose your style
            </label>
            <div className="tone-buttons">
              <button
                onClick={() => setTone("formal")}
                className={`tone-btn ${tone === "formal" ? "tone-btn-active" : ""}`}
              >
                <div className="tone-icon">🎯</div>
                Professional
              </button>
              <button
                onClick={() => setTone("informal")}
                className={`tone-btn ${tone === "informal" ? "tone-btn-active" : ""}`}
              >
                <div className="tone-icon">😊</div>
                Friendly
              </button>
            </div>
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGenerate}
            disabled={loading || !topic.trim()}
            className={`generate-btn ${loading || !topic.trim() ? "generate-btn-disabled" : ""}`}
          >
            {loading ? (
              <div className="btn-content">
                <div className="spinner"></div>
                Generating Magic...
              </div>
            ) : (
              <div className="btn-content">
                <span className="btn-icon">✨</span>
                Generate Presentation
              </div>
            )}
          </button>

          {/* Progress Bar */}
          {loading && (
            <div className="progress-container">
              <div className="progress-text">
                <span>Creating your presentation...</span>
                <span>{Math.round(progress)}%</span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
            </div>
          )}

          {/* Download Button */}
          {pptBlob && !loading && (
            <button
              onClick={downloadPPT}
              className="download-btn"
            >
              <div className="btn-content">
                <span className="btn-icon">📥</span>
                Download Your PPT
              </div>
            </button>
          )}

          {/* Error Message */}
          {error && (
            <div className="error-container">
              <div className="error-content">
                <span className="error-icon">⚠️</span>
                <div className="error-text">
                  <p className="error-title">Oops! Something went wrong</p>
                  <p className="error-message">{error}</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="footer">
          <p className="footer-text">
            Powered by AI • Create professional presentations instantly
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;