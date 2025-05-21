🧠 Text to PPT Generator
Text to PPT Generator is a GenAI-powered tool that helps users convert any topic or text into a structured, professional-looking PowerPoint presentation in seconds. It uses OpenAI's GPT API to generate slide content and python-pptx to build downloadable .pptx files.

📌 Features
Convert text input or topic into well-structured slides

Auto-generate titles, bullet points, and summaries

Choose presentation tone (formal, educational, persuasive, etc.)

Download presentation as a .pptx file

Simple and clean web-based UI

🚀 Technologies Used
Layer	Tools/Frameworks
Frontend	React / HTML / Tailwind CSS
Backend	Python, FastAPI
AI Service	OpenAI GPT API
Slide Builder	python-pptx
Security	HTTPS, API key stored via .env
Deployment	GitHub + Vercel/Render (optional)

📂 Project Structure
bash
Copy
Edit
text-to-ppt/
├── frontend/           # React-based UI
├── backend/            # FastAPI service
│   ├── main.py         # API logic
│   └── ppt_generator.py
├── prompts/            # Custom GPT prompt templates
├── .env.example        # API key format
└── README.md
⚙️ Setup Instructions
Clone the repo:

bash
Copy
Edit
git clone https://github.com/your-username/text-to-ppt.git
cd text-to-ppt
Set up backend:

bash
Copy
Edit
cd backend
pip install -r requirements.txt
cp .env.example .env  # Add your OpenAI API key
uvicorn main:app --reload
Set up frontend (optional):

bash
Copy
Edit
cd frontend
npm install
npm start
🔐 Security & Privacy
API keys are secured via .env file

No input data is stored on the server

HTTPS recommended in deployment

✅ To-Do / Enhancements
Add support for exporting to Google Slides

Theme selection for slide design

Multi-language support

📄 License
This project is open source and available under the MIT License.

