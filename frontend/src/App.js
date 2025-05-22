import React, { useState } from "react";
import "./App.css"; // ✅ Import external CSS

function App() {
  const [topic, setTopic] = useState("");
  const [tone, setTone] = useState("formal");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [pptBlob, setPptBlob] = useState(null);

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

  return (
    <div className="container">
      <div className="main-card">
        <h1 className="title">🎨 AI Text to PPT Generator</h1>

        <div className="form-group">
          <input
            type="text"
            className="form-control"
            placeholder="Enter topic (e.g., Climate Change, Machine Learning)"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
          />
        </div>

        <div className="form-group">
          <select
            className="form-select"
            value={tone}
            onChange={(e) => setTone(e.target.value)}
          >
            <option value="formal">🎯 Formal & Professional</option>
            <option value="informal">😊 Casual & Friendly</option>
          </select>
        </div>

        <button
          className="btn btn-primary"
          onClick={handleGenerate}
          disabled={loading || !topic.trim()}
        >
          {loading ? (
            <>
              <span
                className="spinner-border spinner-border-sm"
                role="status"
                aria-hidden="true"
              ></span>
              Generating...
            </>
          ) : (
            "✨ Generate PPT"
          )}
        </button>

        {pptBlob && (
          <button className="btn btn-success" onClick={downloadPPT}>
            📥 Download PPT
          </button>
        )}

        {error && (
          <div className="alert alert-danger" role="alert">
            <strong>❌ Error:</strong> {error}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
