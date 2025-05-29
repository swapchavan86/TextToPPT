// frontend/src/App.js
import React, { useState, useEffect, useCallback } from 'react';
import './App.css';

function App() {
  const [topic, setTopic] = useState("");
  const [tone, setTone] = useState("educational");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [downloadUrl, setDownloadUrl] = useState("");
  const [progress, setProgress] = useState(0);
  const [operationMessage, setOperationMessage] = useState("");
  const [isFormValid, setIsFormValid] = useState(false);

  // Form validation effect (from first file)
  useEffect(() => {
    setIsFormValid(topic.trim().length > 0);
  }, [topic]);

  // Effect to stop loading when operation completes (from first file)
  useEffect(() => {
    if (downloadUrl || error) {
      setLoading(false);
      if (downloadUrl && !error) {
        setProgress(100);
        setOperationMessage("Presentation ready for download!");
      } else if (error) {
        setProgress(0);
      }
    }
  }, [downloadUrl, error]);

  // Enhanced progress simulation (from first file)
  const simulateProgress = useCallback(() => {
    setProgress(0);
    setOperationMessage("Initializing AI engine...");
    let currentProgress = 0;
    const intervalId = setInterval(() => {
      if (!loading && !downloadUrl) {
          clearInterval(intervalId);
          if (!error) setProgress(0);
          if (!error) setOperationMessage("");
          return;
      }

      currentProgress += Math.random() * 8 + 5;

      if (downloadUrl) {
        setProgress(100);
        setOperationMessage("Finalizing presentation...");
        clearInterval(intervalId);
        return;
      }

      if (currentProgress >= 95) {
        setProgress(95);
        setOperationMessage("Applying final touches...");
      } else {
        setProgress(currentProgress);
        if (currentProgress < 25) setOperationMessage("Analyzing your content...");
        else if (currentProgress < 50) setOperationMessage("Generating slide layouts...");
        else if (currentProgress < 75) setOperationMessage("Crafting visual elements...");
        else setOperationMessage("Assembling presentation...");
      }
    }, 400);
    return intervalId;
  }, [loading, downloadUrl, error]);

  // Complete API connection logic from first file
  const handleGenerate = async () => {
    console.log("handleGenerate called");
    setLoading(true);
    setError("");
    setDownloadUrl("");
    setOperationMessage("Starting generation...");

    const progressInterval = simulateProgress();

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";
      const requestBody = {
        topic: topic,
        tone: tone,
      };
      console.log("Sending request to backend:", `${backendUrl}/generate-ppt/`, "with body:", JSON.stringify(requestBody));

      const response = await fetch(`${backendUrl}/generate-ppt/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });

      console.log("Backend response status:", response.status, response.statusText);

      if (!response.ok) {
        let errorMessage = `Request failed: ${response.statusText} (${response.status})`;
        try {
            const responseData = await response.json();
            console.log("Backend error response data:", responseData);
            if (responseData && responseData.detail) {
              if (Array.isArray(responseData.detail) && responseData.detail[0] && responseData.detail[0].msg) {
                errorMessage = responseData.detail[0].msg;
              } else if (typeof responseData.detail === 'string') {
                errorMessage = responseData.detail;
              }
            } else if (responseData && responseData.message) {
                errorMessage = responseData.message;
            }
        } catch (jsonError) {
            console.warn("Could not parse error response as JSON:", jsonError);
        }
        console.error("API Error from backend:", errorMessage);
        throw new Error(errorMessage);
      }

      const blob = await response.blob();
      if (blob.size === 0) {
        console.error("Backend response OK, but blob is empty.");
        throw new Error("Server returned an empty presentation file.");
      }
      const url = window.URL.createObjectURL(blob);
      setDownloadUrl(url);
      console.log("Blob URL created for download:", url);

    } catch (err) {
      console.error("Error in handleGenerate (fetch or processing):", err);
      setError(err.message || "An unknown error occurred during generation.");
    } finally {
        clearInterval(progressInterval);
    }
  };

  // Download trigger logic from first file
  const triggerDownload = () => {
    if (downloadUrl) {
      console.log("Attempting to trigger download for URL:", downloadUrl);
      setOperationMessage("Preparing download...");
      const anchor = document.createElement('a');
      anchor.href = downloadUrl;
      const filename = `${topic.substring(0,30).replace(/\s+/g, '_') || "presentation"}.pptx`;
      anchor.download = filename; 
      document.body.appendChild(anchor);
      anchor.click();
      document.body.removeChild(anchor);
      setOperationMessage("Download initiated!");
    } else {
      console.log("No download URL available to trigger download.");
      setError("Download URL is not available. Please try generating again.");
    }
  };

  // Data from second file
  const exampleTopics = [
    "Effective Time Management Strategies", 
    "Introduction to Quantum Computing", 
    "The Future of Renewable Energy Sources",
    "Content Marketing for Small Businesses", 
    "Mindfulness and Well-being in the Workplace"
  ];

  const availableTones = [
    { key: "educational", name: "Educational", icon: "🎓" },
    { key: "formal", name: "Formal", icon: "👔" },
    { key: "casual", name: "Casual", icon: "😊" },
    { key: "professional", name: "Professional", icon: "💼" },
    { key: "enthusiastic", name: "Enthusiastic", icon: "🎉" },
  ];

  // UI Design from second file (completely unchanged)
  return (
    <div className="min-vh-100 bg-gradient-primary">
      {/* Navigation */}
      <nav className="navbar navbar-expand-lg navbar-dark bg-transparent">
        <div className="container">
          <a className="navbar-brand d-flex align-items-center" href="#">
            <div className="brand-icon me-2">
              <i className="fas fa-magic"></i>
            </div>
            <span className="brand-text">PowerPoint AI</span>
          </a>
          <div className="d-flex align-items-center">
            <span className="badge bg-white text-primary px-3 py-2 rounded-pill">
              <i className="fas fa-robot me-1"></i>
              AI Powered
            </span>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-lg-8 col-xl-7">
            {/* Hero Section */}
            <div className="text-center mb-5">
              <div className="hero-icon">
                <div className="icon-wrapper">
                  <i className="fas fa-file-powerpoint"></i>
                </div>
              </div>
              <h1 className="hero-title text-white">
                Transform Ideas into 
                <span className="text-warning"> Stunning Presentations</span>
              </h1>
              <p className="hero-subtitle text-white-50">
                Harness the power of AI to create professional PowerPoint presentations in seconds. 
                Just describe your topic and let our advanced AI do the rest.
              </p>
              <div className="hero-stats d-flex justify-content-center gap-4 mb-5">
                <div className="stat-item">
                  <div className="stat-number text-warning">10K+</div>
                  <div className="stat-label text-white-50">Presentations</div>
                </div>
                <div className="stat-item">
                  <div className="stat-number text-warning">30s</div>
                  <div className="stat-label text-white-50">Avg. Time</div>
                </div>
                <div className="stat-item">
                  <div className="stat-number text-warning">5⭐</div>
                  <div className="stat-label text-white-50">Rating</div>
                </div>
              </div>
            </div>

            {/* Main Card */}
            <div className="card main-card border-0 shadow-lg">
              <div className="card-body p-4 p-md-5">
                {/* Alert Messages */}
                {error && (
                  <div className="alert alert-danger alert-dismissible fade show mb-4" role="alert">
                    <div className="d-flex align-items-start">
                      <i className="fas fa-exclamation-triangle me-3 mt-1"></i>
                      <div className="flex-grow-1">
                        <h6 className="alert-heading mb-1">Oops! Something went wrong</h6>
                        <p className="mb-0 small">{error}</p>
                      </div>
                      <button type="button" className="btn-close" onClick={() => setError('')}></button>
                    </div>
                  </div>
                )}

                {downloadUrl && !loading && !error && (
                  <div className="alert alert-success alert-dismissible fade show mb-4" role="alert">
                    <div className="d-flex align-items-center">
                      <i className="fas fa-check-circle me-3"></i>
                      <div className="flex-grow-1">
                        <h6 className="alert-heading mb-1">🎉 Your presentation is ready!</h6>
                        <p className="mb-0 small">Click the download button below to get your PowerPoint file.</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Topic Input */}
                <div className="form-section">
                  <label className="form-label">
                    <i className="fas fa-lightbulb text-warning me-2"></i>
                    What's your presentation topic?
                  </label>
                  <div className="position-relative">
                    <textarea
                      className="form-control form-control-lg topic-input"
                      placeholder="e.g., The Future of Renewable Energy: Innovations and Challenges"
                      value={topic}
                      onChange={(e) => setTopic(e.target.value)}
                      rows={4}
                      disabled={loading}
                    />
                    {topic && !loading && (
                      <div className="input-success-indicator">
                        <i className="fas fa-check-circle text-success"></i>
                      </div>
                    )}
                  </div>
                  
                  {/* Character count */}
                  <div className="form-text mt-2">
                    <small className="text-muted">
                      <i className="fas fa-info-circle me-1"></i>
                      Characters: {topic.length} | Be descriptive for better results
                    </small>
                  </div>

                  {/* Example Topics */}
                  {!topic && !loading && (
                    <div className="suggestions-section mt-3">
                      <p className="suggestions-label">
                        <i className="fas fa-star text-warning me-1"></i>
                        <strong>Popular topics:</strong>
                      </p>
                      <div className="suggestions-grid">
                        {exampleTopics.slice(0, 3).map((example, idx) => (
                          <button 
                            key={idx} 
                            onClick={() => setTopic(example)} 
                            className="btn btn-outline-primary btn-sm suggestion-chip"
                          >
                            {example}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Tone Selection */}
                <div className="form-section">
                  <label className="form-label">
                    <i className="fas fa-palette text-primary me-2"></i>
                    Choose your presentation style:
                  </label>
                  <div className="tone-grid">
                    {availableTones.map((toneItem) => (
                      <button
                        key={toneItem.key}
                        onClick={() => setTone(toneItem.key)}
                        className={`tone-option ${tone === toneItem.key ? 'tone-option-active' : ''}`}
                        disabled={loading}
                      >
                        <div className="tone-emoji">{toneItem.icon}</div>
                        <span className="tone-name">{toneItem.name}</span>
                        {tone === toneItem.key && (
                          <div className="tone-check">
                            <i className="fas fa-check"></i>
                          </div>
                        )}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Generate Button */}
                <div className="d-grid mb-4">
                  <button
                    onClick={handleGenerate}
                    disabled={loading || !topic.trim()}
                    className={`btn btn-lg generate-button ${loading || !topic.trim() ? 'disabled' : ''}`}
                  >
                    {loading ? (
                      <div className="d-flex align-items-center justify-content-center">
                        <div className="spinner-border spinner-border-sm me-2" role="status">
                          <span className="visually-hidden">Loading...</span>
                        </div>
                        <span>Generating Magic...</span>
                      </div>
                    ) : (
                      <div className="d-flex align-items-center justify-content-center">
                        <i className="fas fa-magic me-2"></i>
                        <span>Generate Presentation</span>
                      </div>
                    )}
                  </button>
                </div>

                {/* Progress Section */}
                {(loading || progress > 0) && (
                  <div className="progress-section mb-4">
                    <div className="d-flex justify-content-between align-items-center mb-2">
                      <span className="progress-label">{operationMessage || "Processing..."}</span>
                      <span className="progress-percentage">{Math.round(progress)}%</span>
                    </div>
                    <div className="progress progress-custom">
                      <div 
                        className="progress-bar progress-bar-animated" 
                        style={{ width: `${progress}%` }}
                      ></div>
                    </div>
                  </div>
                )}

                {/* Download Button */}
                {downloadUrl && !loading && !error && (
                  <div className="d-grid">
                    <button 
                      onClick={triggerDownload} 
                      className="btn btn-success btn-lg download-button"
                    >
                      <div className="d-flex align-items-center justify-content-center">
                        <i className="fas fa-download me-2"></i>
                        <span>Download Your PowerPoint</span>
                      </div>
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Features Section */}
            <div className="features-section mt-5">
              <div className="row g-4">
                <div className="col-md-4">
                  <div className="feature-item text-center">
                    <div className="feature-icon mb-3">
                      <i className="fas fa-bolt"></i>
                    </div>
                    <h6 className="feature-title text-white mb-2">Lightning Fast</h6>
                    <p className="feature-desc text-white-50 small">
                      Generate presentations in under 30 seconds with our optimized AI engine.
                    </p>
                  </div>
                </div>
                <div className="col-md-4">
                  <div className="feature-item text-center">
                    <div className="feature-icon mb-3">
                      <i className="fas fa-paint-brush"></i>
                    </div>
                    <h6 className="feature-title text-white mb-2">Professional Design</h6>
                    <p className="feature-desc text-white-50 small">
                      Beautiful layouts and themes automatically applied to your content.
                    </p>
                  </div>
                </div>
                <div className="col-md-4">
                  <div className="feature-item text-center">
                    <div className="feature-icon mb-3">
                      <i className="fas fa-shield-alt"></i>
                    </div>
                    <h6 className="feature-title text-white mb-2">Secure & Private</h6>
                    <p className="feature-desc text-white-50 small">
                      Your data is processed securely and never stored on our servers.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="text-center py-4 mt-5">
        <div className="container">
          <p className="text-white-50 mb-0">
            <i className="fas fa-heart text-danger me-1"></i>
            Powered by Advanced AI Technology
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;