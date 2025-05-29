// frontend/src/App.js
import React, { useState, useEffect, useCallback } from 'react';
import './App.css';

function App() {
  const [topic, setTopic] = useState(""); // Changed from textInput
  const [tone, setTone] = useState("educational"); // Added, default "educational"
  // numSlides state removed

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [downloadUrl, setDownloadUrl] = useState("");
  const [progress, setProgress] = useState(0);
  const [operationMessage, setOperationMessage] = useState("");

  // Effect to stop loading when operation completes (success or error)
  useEffect(() => {
    if (downloadUrl || error) {
      setLoading(false);
      if (downloadUrl && !error) {
        setProgress(100); // Ensure progress is 100 on success
        setOperationMessage("Presentation ready for download!");
      } else if (error) {
        setProgress(0); // Reset progress on error
        // Operation message will be the error itself
      }
    }
  }, [downloadUrl, error]);

  // Simulate progress for better UX
  const simulateProgress = useCallback(() => {
    setProgress(0);
    setOperationMessage("Initializing...");
    let currentProgress = 0;
    const intervalId = setInterval(() => {
      // Stop simulating if no longer loading (e.g., error occurred early or user cancelled)
      if (!loading && !downloadUrl) { // Check loading state from parent scope
          clearInterval(intervalId);
          if (!error) setProgress(0); // Reset if not an error state
          if (!error) setOperationMessage("");
          return;
      }

      currentProgress += Math.random() * 10 + 7; // Slightly faster and more consistent steps

      if (downloadUrl) { // If downloadUrl is set, we are done with generation
        setProgress(100);
        setOperationMessage("Finalizing and preparing download...");
        clearInterval(intervalId);
        return;
      }

      if (currentProgress >= 95) {
        setProgress(95);
        setOperationMessage("Almost ready, wrapping up...");
        // Don't clear interval here, wait for downloadUrl or error to stop it
      } else {
        setProgress(currentProgress);
        if (currentProgress < 30) setOperationMessage("Contacting AI service...");
        else if (currentProgress < 70) setOperationMessage("AI is crafting your content...");
        else setOperationMessage("Assembling presentation slides...");
      }
    }, 450); // Interval duration
    return intervalId;
  }, [loading, downloadUrl, error]); // Dependencies for useCallback


  const handleGenerate = async () => {
    console.log("handleGenerate called");
    setLoading(true); // Set loading true immediately
    setError("");
    setDownloadUrl("");
    setOperationMessage("Starting generation..."); // Initial message

    const progressInterval = simulateProgress();

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";
      const requestBody = {
        topic: topic, // Changed from textInput
        tone: tone,   // Added
      };
      console.log("Sending request to backend:", `${backendUrl}/generate-ppt/`, "with body:", JSON.stringify(requestBody));

      // The backend directly streams the file, so we handle the response differently.
      const response = await fetch(`${backendUrl}/generate-ppt/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });

      console.log("Backend response status:", response.status, response.statusText);

      if (!response.ok) {
        // Attempt to parse error response as JSON
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
            } else if (responseData && responseData.message) { // Fallback for other error structures
                errorMessage = responseData.message;
            }
        } catch (jsonError) {
            // If error response is not JSON, use the status text.
            console.warn("Could not parse error response as JSON:", jsonError);
        }
        console.error("API Error from backend:", errorMessage);
        throw new Error(errorMessage);
      }

      // If response is OK, it should be a file stream
      const blob = await response.blob();
      if (blob.size === 0) {
        console.error("Backend response OK, but blob is empty.");
        throw new Error("Server returned an empty presentation file.");
      }
      const url = window.URL.createObjectURL(blob);
      setDownloadUrl(url); // This will trigger useEffect for loading and progress
      // Progress and operation message will be updated by useEffect and simulateProgress final step
      console.log("Blob URL created for download:", url);


    } catch (err) {
      console.error("Error in handleGenerate (fetch or processing):", err);
      setError(err.message || "An unknown error occurred during generation.");
      // setLoading(false) and progress reset will be handled by useEffect due to setError
    } finally {
        clearInterval(progressInterval);
    }
  };

  const triggerDownload = () => {
    if (downloadUrl) {
      console.log("Attempting to trigger download for URL:", downloadUrl);
      setOperationMessage("Download starting...");
      const anchor = document.createElement('a');
      anchor.href = downloadUrl;
      // Use topic for filename
      const filename = `${topic.substring(0,30).replace(/\s+/g, '_') || "presentation"}.pptx`;
      anchor.download = filename; 
      document.body.appendChild(anchor);
      anchor.click();
      document.body.removeChild(anchor);
      // window.URL.revokeObjectURL(downloadUrl); // Clean up the object URL
      setOperationMessage("Download initiated!");
      // Optionally reset downloadUrl if you want the button to disappear after one click
      // setTimeout(() => { setDownloadUrl(""); window.URL.revokeObjectURL(downloadUrl); }, 2000); 
    } else {
      console.log("No download URL available to trigger download.");
      setError("Download URL is not available. Please try generating again.");
    }
  };

  const exampleTopics = [
    "Effective Time Management Strategies", "Introduction to Quantum Computing", "The Future of Renewable Energy Sources",
    "Content Marketing for Small Businesses", "Mindfulness and Well-being in the Workplace"
  ];

  const availableTones = [
    { key: "educational", name: "Educational", icon: "🎓" },
    { key: "formal", name: "Formal", icon: "👔" },
    { key: "casual", name: "Casual", icon: "😊" },
    { key: "professional", name: "Professional", icon: "💼" },
    { key: "enthusiastic", name: "Enthusiastic", icon: "🎉" },
  ];

  return (
    <div className="app-container">
      <div className="app-wrapper">
        <div className="main-card">
          <div className="bg-element bg-element-1"></div>
          <div className="bg-element bg-element-2"></div>
          <div className="header">
            <div className="icon-container"><span className="icon">🎨</span></div>
            <h1 className="title">AI PowerPoint Generator</h1>
            <p className="subtitle">Transform your ideas into presentations instantly</p>
          </div>

          <div className="form-group">
            <label className="form-label">📝 What's your presentation topic?</label>
            <div className="input-container">
              <textarea
                className="form-input"
                placeholder="e.g., The future of renewable energy"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                rows={5}
                disabled={loading}
              />
              {topic && !loading && (<div className="input-check">✓</div>)}
            </div>
            {!topic && !loading && (
              <div className="suggestions">
                <p className="suggestions-label">💡 Try these examples (you can expand on them in the text area):</p>
                <div className="suggestions-list">
                  {exampleTopics.slice(0, 3).map((example, idx) => (
                    <button key={idx} onClick={() => setTopic(example)} className="suggestion-btn">{example}</button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Tone Selection UI */}
          <div className="form-group">
            <label className="form-label">🎭 Choose your style:</label>
            <div className="tone-buttons">
              {availableTones.map((toneItem) => (
                <button
                  key={toneItem.key}
                  onClick={() => setTone(toneItem.key)}
                  className={`tone-btn ${tone === toneItem.key ? "tone-btn-active" : ""}`}
                  disabled={loading}
                >
                  <div className="tone-icon">{toneItem.icon}</div>
                  {toneItem.name}
                </button>
              ))}
            </div>
          </div>
          
          {/* Number of Slides input removed */}

          <button
            onClick={handleGenerate}
            disabled={loading || !topic.trim()} // Depends on topic now
            className={`generate-btn ${loading || !topic.trim() ? "generate-btn-disabled" : ""}`}
          >
            {loading ? (
              <div className="btn-content"><div className="spinner"></div>Generating...</div>
            ) : (
              <div className="btn-content"><span className="btn-icon">✨</span>Generate Presentation</div>
            )}
          </button>

          {(loading || progress > 0) && (
            <div className="progress-container">
              <div className="progress-text">
                <span>{operationMessage || (loading ? "Processing..." : "Done!")}</span>
                <span>{Math.round(progress)}%</span>
              </div>
              <div className="progress-bar"><div className="progress-fill" style={{ width: `${progress}%` }}></div></div>
            </div>
          )}

          {downloadUrl && !loading && !error && (
            <button onClick={triggerDownload} className="download-btn">
              <div className="btn-content"><span className="btn-icon">📥</span>Download Your PPT</div>
            </button>
          )}

          {error && !loading && (
            <div className="error-container">
              <div className="error-content">
                <span className="error-icon">⚠️</span>
                <div className="error-text">
                  <p className="error-title">An Error Occurred</p>
                  <p className="error-message">{error}</p>
                </div>
              </div>
            </div>
          )}
        </div>
        <div className="footer"><p className="footer-text">Powered by Generative AI</p></div>
      </div>
    </div>
  );
}

export default App;