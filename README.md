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
| Frontend     | React / HTML / Tailwind CSS   |
| Backend      | Python, FastAPI               |
| AI Service   | OpenAI GPT API                |
| Slide Builder| python-pptx                   |
| Security     | HTTPS, API key in `.env`      |
| Deployment   | GitHub + Vercel/Render (opt)  |

---

##  OpenAPI Documentation
The backend API provides standard OpenAPI documentation. Once the backend server is running (e.g., with `uvicorn backend.main:app --reload --port 8000`), you can access:
- Swagger UI at [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc at [http://localhost:8000/redoc](http://localhost:8000/redoc)

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

## 🛠️ Dependencies & Setup

### Backend
Located in the `backend/` directory.
- Key dependencies: `fastapi`, `uvicorn`, `python-pptx`, `openai`, `python-dotenv`
- Test dependencies: `pytest`, `httpx`, `pytest-mock`
- All backend and test dependencies are listed in `backend/requirements.txt`.
- Setup:
  ```bash
  # Clone the repository first if you haven't:
  # git clone https://github.com/your-username/text-to-ppt.git # Replace with actual URL
  # cd text-to-ppt

  cd backend
  python -m venv venv
  venv\\Scripts\\activate          # On Windows
  pip install -r requirements.txt
  # Create a .env file (e.g., by copying .env.example if provided, or manually).
  # It should contain your Secure API key:
  # AZURE_OPENAI_API_KEY='your_Secure_api_key_here'
  #AZURE_OPENAI_ENDPOINT='<<SecureAPIEndPoint>>'
  #OPENAI_API_VERSION=2024-02-01 or Latest
  #AZURE_OPENAI_DEPLOYMENT_NAME=<<Gpt Model>>
  #REDIS_URL=redis://localhost:6379
```
Set Python path for local imports (required for both running and testing):
```bash
  $env:PYTHONPATH="<<ProjectPath>>\backend"
```
Run backend server:
```bash
  uvicorn backend.main:app --reload --port 8000
```
```bash
  # The tests use a base URL for the server, which defaults to http://127.0.0.1:8000.
  # If your server runs on a different URL during testing, set it in your .env file:
  # PYTEST_BASE_URL='http://your_test_server_url:port'
  cd ..
```
🧪### **Running Tests**
Install test dependencies:
```bash
  pip install -r requirements.txt
```
Make sure the backend is not rate-limited during test:
  Add this line before running tests:
    ```bash
      $env:TESTING=true
    ```
Run tests from the project root:
    ```bash
      pytest tests/
    ```
###🧱 **Redis Setup (Required for Rate Limiting)**
  Redis is used by fastapi-limiter to enforce API request limits.
  Option 1: Run Redis using Docker (Recommended)
    Install Docker Desktop: https://www.docker.com/products/docker-desktop
    Start Docker and run Redis:
    ```bash
      docker run -d -p 6379:6379 --name redis-server redis
    ```
### Frontend
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
*   The FastAPI backend server **must be running** before executing the tests. Start it from the `backend` directory:
    ```bash
    cd backend
    uvicorn main:app --reload --port 8000 
    # Or your usual command to start the server
    cd .. 
    ```
*   Ensure all backend dependencies, including test dependencies, are installed:
    ```bash
    pip install -r backend/requirements.txt
    ```

**Running Tests:**
From the **project root directory**, run:
```bash
pytest tests/test_main.py
```

**Note on OpenAI Calls:**
The tests are configured to **mock** calls to the OpenAI API. This means they do not make actual calls to OpenAI, ensuring they run quickly, reliably, and without incurring API costs or hitting rate limits. The mocking simulates successful responses from OpenAI for testing the application's internal logic.

---

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
