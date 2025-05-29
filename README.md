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

## 📖 OpenAPI Documentation

The FastAPI backend provides automatically generated API documentation compliant with the OpenAPI Specification. You can access it through the following URLs when the backend server is running:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

These interfaces allow you to interactively explore the API endpoints, view request/response models, and test the API.

---

## 📂 Project Structure

The project is organized as follows:

<pre>text-to-ppt/
├── backend/                 # Contains the FastAPI backend application
│   ├── main.py              # Core API logic for presentation generation
│   └── requirements.txt     # Python dependencies for the backend
├── frontend/                # Contains the React-based frontend application
│   ├── public/              # Public assets for the frontend
│   ├── src/                 # Frontend source code (React components, etc.)
│   ├── package.json         # Frontend dependencies and scripts
│   └── ... (other frontend files like package-lock.json)
├── tests/                   # Contains backend API tests
│   └── test_main.py         # Pytest tests for the API endpoints
├── .gitignore               # Specifies intentionally untracked files
├── README.md                # This file
└── ... (other root files like gitattributes)
</pre>

- **`backend/`**: Houses the Python FastAPI application that handles API requests, interacts with the OpenAI API, and generates `.pptx` files.
- **`frontend/`**: Contains the React application that provides the user interface for interacting with the Text to PPT Generator.
- **`tests/`**: Includes integration tests for the backend API, ensuring endpoints behave as expected.

---

## 🛠️ Dependencies

The project's dependencies are managed separately for the backend and frontend.

### Backend Dependencies (`backend/requirements.txt`)
The backend relies on Python and its dependencies are listed in `backend/requirements.txt`. Key dependencies include:
- `fastapi`: For building the API.
- `uvicorn`: For running the FastAPI server.
- `python-pptx`: For generating PowerPoint presentations.
- `openai`: For interacting with the OpenAI API.
- `python-dotenv`: For managing environment variables (like API keys).
- `pytest`: For running tests.
- `httpx`: For making HTTP requests within tests.

### Frontend Dependencies (`frontend/package.json`)
The frontend is a React application. Its dependencies are managed using `npm` and are listed in `frontend/package.json`. Key dependencies include:
- `react`
- `tailwindcss` (or other relevant UI libraries based on `package.json`)

### Testing Dependencies
Dependencies required for running tests, such as `pytest` and `httpx`, are included in the `backend/requirements.txt` file.

---

## ⚙️ Setup Instructions

# 1. Clone the repo
```bash
git clone https://github.com/your-username/text-to-ppt.git # Replace with the actual repo URL if different
cd text-to-ppt
```

# 2. Set up Backend
```bash
cd backend
pip install -r requirements.txt
# Create a .env file from .env.example (if provided) or manually set your OpenAI API key
# Example: cp .env.example .env 
# Then, add your OPENAI_API_KEY to the .env file.
# Ensure your .env file is in the /backend directory.
uvicorn main:app --reload
```
The backend server will typically start on `http://localhost:8000`.

# 3. Set up Frontend (Optional)
```bash
cd frontend # Navigate from the root directory
npm install
npm start
```
The frontend development server will typically start on `http://localhost:3000`.

---

## 🧪 Testing

This project includes integration tests for the backend API. These tests verify the functionality of the `/generate-ppt/` endpoint.

**Prerequisites:**
- Ensure all backend dependencies, including `pytest` and `httpx`, are installed by running `pip install -r backend/requirements.txt` from the `backend` directory (or project root, adjusting path).
- **The backend server must be running** for the tests to execute, as they make live requests to the API. Start the backend server using `uvicorn main:app --reload` in the `backend` directory.

**Running Tests:**
1. Navigate to the project root directory (`text-to-ppt/`).
2. Run the tests using Pytest:
   ```bash
   pytest tests/test_main.py
   ```
   Or, to run all tests discovered by Pytest (if configuration allows):
   ```bash
   pytest
   ```

Test results will be displayed in your terminal.

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
