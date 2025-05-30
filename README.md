# 🧠 Text to PPT Generator

**Text to PPT Generator** is a GenAI-powered tool that helps users convert any topic or text into a structured, professional-looking PowerPoint presentation in seconds. It uses Google's Generative AI to generate slide content and `python-pptx` to build downloadable `.pptx` files.

---
## 📽️ Demo Video
[![Watch Demo with Autoplay](https://img.youtube.com/vi/F01J5kqZVgU/hqdefault.jpg)](https://youtu.be/F01J5kqZVgU&autoplay=1)

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
| AI Service   | Google Generative AI (Gemini) |
| Slide Builder| python-pptx                   |
| Security     | HTTPS, API key in `.env`      |
| Deployment   | GitHub + Vercel/Render (opt)  |

---

## 📂 Project Structure

<pre>text-to-ppt/
├── backend/ # FastAPI service
│   ├── assets/
│   ├── init.py
│   ├── ai_services.py
│   ├── config.py
│   ├── main.py # API logic
│   ├── models.py
│   ├── ppt_utils.py
│   ├── requirements.txt
│   └── .env (user-created for API keys)
├── frontend/ # React-based UI
│   ├── public/
│   ├── src/
│   └── package.json
├── tests
│   ├── test_ai_services.py
├── logs/
├── .gitattributes
├── .gitignore
├── package-lock.json
├── package.json
└── README.md
</pre>

⚙️ Setup Instructions

#!/bin/bash

# 1. Clone the repo
```bash
git clone https://github.com/swapchavan86/text-to-ppt.git
cd text-to-ppt
```
# 2. Set up backend
```bash
cd backend
pip install -r requirements.txt
# Create a .env file (e.g., by copying from a template if provided, or creating one manually)
# and add your Google API key like this:
# GOOGLE_API_KEY="your_google_api_key_here"
# Alternatively, ensure GOOGLE_API_KEY is set as an environment variable.
uvicorn main:app --reload
```
# 2. Set up frontend (Optional)
```bash
cd frontend
npm install
npm start
```

## 🔐 Security & Privacy

API keys stored in .env file
No user input is stored
Use HTTPS for secure communication

## ✅ To-Do / Enhancements

Export to Google Slides
Theme customization for slides
Multi-language support

## 📄 License
This project is open source under the MIT License.
