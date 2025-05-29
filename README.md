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

<pre>text-to-ppt/
├── backend/
│   ├── pycache/
│   ├── .pytest_cache/
│   ├── assets/
│   ├── generated_files/
│   ├── init.py
│   ├── .env (user-created for API keys)
│   ├── main.py
│   ├── models.py
│   ├── openai_service.py
│   ├── ppt_utils.py
│   ├── requirements.txt
│   └── venv/
│       ├── Include/
│       ├── Lib/
│       └── Scripts/
├── frontend/
│   ├── public/
│   ├── src/
│   └── package.json
├── tests/
│   ├── pycache/
│   └── test_main.py
├── .gitignore
├── pyvenv.cfg
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
  pip install -r requirements.txt
  # Create a .env file (e.g., by copying .env.example if provided, or manually).
  # It should contain your OpenAI API key:
  # OPENAI_API_KEY='your_openai_api_key_here'
  #
  # The tests use a base URL for the server, which defaults to http://127.0.0.1:8000.
  # If your server runs on a different URL during testing, set it in your .env file:
  # PYTEST_BASE_URL='http://your_test_server_url:port'
  cd ..
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
