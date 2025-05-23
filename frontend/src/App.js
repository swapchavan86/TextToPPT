// frontend/src/App.js
import React, { useState, useEffect, useCallback } from 'react';
import './App.css';

function App() {
  const [textInput, setTextInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [downloadUrl, setDownloadUrl] = useState("");
  const [progress, setProgress] = useState(0);
  const [numSlides, setNumSlides] = useState(5);
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
        text_input: textInput,
        num_slides: parseInt(numSlides) || 5,
      };
      console.log("Sending request to backend:", `${backendUrl}/generate-ppt/`, "with body:", JSON.stringify(requestBody));

      const response = await fetch(`${backendUrl}/generate-ppt/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });
      
      console.log("Backend response status:", response.status, response.statusText);
      const responseData = await response.json(); // Attempt to parse JSON for both success and error
      console.log("Backend response data:", responseData);

      if (!response.ok) {
        // Try to get a more specific error message from FastAPI's detail structure
        let errorMessage = `Request failed: ${response.statusText} (${response.status})`;
        if (responseData && responseData.detail) {
          if (Array.isArray(responseData.detail) && responseData.detail[0] && responseData.detail[0].msg) {
            errorMessage = responseData.detail[0].msg;
          } else if (typeof responseData.detail === 'string') {
            errorMessage = responseData.detail;
          }
        } else if (responseData && responseData.message) {
            errorMessage = responseData.message;
        }
        console.error("API Error from backend:", errorMessage);
        throw new Error(errorMessage);
      }

      if (responseData.download_url) {
        setDownloadUrl(responseData.download_url); // This will trigger useEffect
        // Progress and operation message will be updated by useEffect and simulateProgress final step
        console.log("Download URL set from backend:", responseData.download_url);
      } else {
        console.error("Backend response OK, but no download_url found in data:", responseData);
        throw new Error("Server did not provide a download link despite success status.");
      }
      
    } catch (err) {
      console.error("Error in handleGenerate (fetch or processing):", err);
      setError(err.message || "An unknown error occurred during generation.");
      // setLoading(false) and progress reset will be handled by useEffect due to setError
    } finally {
        // Interval must be cleared if it's still running
        // (e.g., if an error occurred before downloadUrl was set)
        clearInterval(progressInterval);
        // setLoading(false) is handled by the useEffect hook based on downloadUrl or error states
    }
  };

  const triggerDownload = () => {
    if (downloadUrl) {
      console.log("Attempting to trigger download for URL:", downloadUrl);
      setOperationMessage("Download starting...");
      const anchor = document.createElement('a');
      anchor.href = downloadUrl;
      const filename = downloadUrl.substring(downloadUrl.lastIndexOf('/') + 1) || `${textInput.substring(0,20) || "presentation"}.pptx`;
      anchor.download = filename; 
      document.body.appendChild(anchor);
      anchor.click();
      document.body.removeChild(anchor);
      setOperationMessage("Download initiated!");
      // Optionally reset downloadUrl if you want the button to disappear after one click
      // setTimeout(() => setDownloadUrl(""), 2000); 
    } else {
      console.log("No download URL available to trigger download.");
      setError("Download URL is not available. Please try generating again.");
    }
  };

  const exampleTopics = [
    "Effective Time Management Strategies", "Introduction to Quantum Computing", "The Future of Renewable Energy Sources",
    "Content Marketing for Small Businesses", "Mindfulness and Well-being in the Workplace"
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
            <p className="subtitle">Transform text into presentations instantly</p>
          </div>

          <div className="form-group">
            <label className="form-label">📝 Enter detailed text or a topic for your presentation:</label>
            <div className="input-container">
              <textarea
                className="form-input"
                placeholder="e.g., A comprehensive analysis of the impact of artificial intelligence on the global economy, covering key sectors like healthcare, finance, and manufacturing, along with potential societal implications and future trends..."
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                rows={5}
                disabled={loading}
              />
              {textInput && !loading && (<div className="input-check">✓</div>)}
            </div>
            {!textInput && !loading && (
              <div className="suggestions">
                <p className="suggestions-label">💡 Try these examples (you can expand on them in the text area):</p>
                <div className="suggestions-list">
                  {exampleTopics.slice(0, 3).map((example, idx) => (
                    <button key={idx} onClick={() => setTextInput(example)} className="suggestion-btn">{example}</button>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="numSlides" className="form-label">⚙️ Number of Content Slides (approx.):</label>
            <input
              type="number"
              id="numSlides"
              className="form-input form-input-small"
              value={numSlides}
              onChange={(e) => setNumSlides(Math.max(1, Math.min(15, parseInt(e.target.value) || 1)))} // Clamp values
              min="1"
              max="15"
              disabled={loading}
            />
          </div>

          <button
            onClick={handleGenerate}
            disabled={loading || !textInput.trim()}
            className={`generate-btn ${loading || !textInput.trim() ? "generate-btn-disabled" : ""}`}
          >
            {loading ? (
              <div className="btn-content"><div className="spinner"></div>Generating...</div>
            ) : (
              <div className="btn-content"><span className="btn-icon">✨</span>Generate Presentation</div>
            )}
          </button>

          {(loading || progress > 0) && ( // Show progress if loading OR if progress was made (e.g. success but before clearing)
            <div className="progress-container">
              <div className="progress-text">
                <span>{operationMessage || (loading ? "Processing..." : "Done!")}</span>
                <span>{Math.round(progress)}%</span>
              </div>
              <div className="progress-bar"><div className="progress-fill" style={{ width: `${progress}%` }}></div></div>
            </div>
          )}

          {downloadUrl && !loading && !error && ( // Show download button only on success
            <button onClick={triggerDownload} className="download-btn">
              <div className="btn-content"><span className="btn-icon">📥</span>Download Your PPT</div>
            </button>
          )}

          {error && !loading && ( // Show error only when not loading
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