# 🧠 Text to PPT Generator

**Text to PPT Generator** is a GenAI-powered tool that helps users convert any topic or text into a structured, professional-looking PowerPoint presentation in seconds. It uses OpenAI's GPT API to generate slide content and `python-pptx` to build downloadable `.pptx` files.

---

## 📌 Features

- Convert text input or topic into well-structured slides  
- Auto-generate titles, bullet points, and summaries  
- Choose presentation tone (formal, educational, persuasive, etc.)  
- Download presentation as a `.pptx` file  
- Simple and clean web-based UI

---

## 🚀 Technologies Used

| Layer        | Tools/Frameworks              |
|--------------|-------------------------------|
| Frontend     | React / HTML / Bootstrap      |
| Backend      | Python, FastAPI               |
| AI Service   | OpenAI GPT API                |
| Slide Builder| python-pptx                   |
| Security     | `.env` for secrets            |
| Testing      | Pytest, pytest-mock           |
| Rate Limiting| Redis, fastapi-limiter        |

---

## 🌐 OpenAPI Documentation

Once the backend server is running, access:

- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)  
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📂 Project Structure

<pre>TextToPPT/
├── backend/ # FastAPI backend
│ ├── main.py # Entry point for FastAPI app
│ ├── models.py # Pydantic data models
│ ├── openai_service.py # Azure OpenAI service integration
│ ├── ppt_utils.py # PPT generation logic using python-pptx
│ ├── init.py
│ └── requirements.txt
├── frontend/ # React-based frontend (Bootstrap styled)
│ ├── src/
│ ├── public/
│ └── package.json
├── tests/ # Pytest test cases for backend
│ └── test_main.py
└── README.md</pre>


---

## 🛠️ Backend Setup

1. Navigate to the backend directory:

    ```bash
    cd backend
    ```

2. Create and activate a virtual environment:

    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # On Windows
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file in `backend/` with:

    ```env
    AZURE_OPENAI_API_KEY=your_secure_api_key_here
    AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
    OPENAI_API_VERSION=2024-02-01
    AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
    REDIS_URL=redis://localhost:6379
    ```

5. Set `PYTHONPATH` before running the backend (required for local module imports):

    ```powershell
    $env:PYTHONPATH="<<ProjectPath>>\backend"
    ```

6. Run backend server:

    ```bash
    uvicorn backend.main:app --reload --port 8000
    ```

---

## 🧪 Running Tests

1. Set environment flag to disable rate limiting:

    ```powershell
    $env:TESTING=true
    ```

2. From project root:

    ```bash
    pytest tests/
    ```

> Tests use mocked OpenAI calls — no real API usage or cost.

---

## 🧱 Redis Setup (For Rate Limiting)

### Option 1: Using Docker (Recommended)

1. Install Docker Desktop: https://www.docker.com/products/docker-desktop  
2. Start Redis container:

    ```bash
    docker run -d -p 6379:6379 --name redis-server redis
    ```

### Option 2: Local Redis Installation (Optional)

**Windows (Chocolatey):**

```bash
choco install redis-64
redis-server
```

## 🌐 Frontend Setup

Located in the `frontend/` directory.
- Uses Node.js and npm.
- Key dependencies: `react` (details in `frontend/package.json`).
- Setup:
  ```bash
  cd frontend
  npm install
  npm start 
  # The frontend will typically be available at http://localhost:3000
  cd ..
  ```

---

## 🧪 Testing
The project includes backend API integration tests using `pytest`. These tests verify the functionality of the `/generate-ppt/` endpoint.

**Prerequisites:**
*   Backend server must be running.
*   ERequired test libraries should be installed.
*   Disable rate limiting for test mode.

**Steps:**
  Set testing environment:
  ```bash
    pytest tests/test_main.py
  ```
  Run tests from the root directory:
  ```bash
    pytest tests/
  ```
**Note on OpenAI Calls:**
OpenAI calls are mocked to avoid real API usage and cost.


## 🔐 Security & Privacy

- API keys should be stored in a `.env` file within the `backend` directory and not committed to version control.
- No user input is stored by the application beyond the immediate processing of the request.
- Use HTTPS for secure communication if deploying to a public server.

---

## ✅ To-Do / Enhancements

- Export to Google Slides
- Theme customization for slides
- Multi-language support

---

## 📄 License
This project is open source under the MIT License.
