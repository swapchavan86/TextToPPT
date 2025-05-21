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

## 📂 Project Structure

<pre>text-to-ppt/
├── frontend/ # React-based UI
├── backend/ # FastAPI service
│ ├── main.py # API logic
│ └── ppt_generator.py
├── prompts/ # GPT prompt templates
├── .env.example # Example API key format
└── README.md</pre>

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
cp .env.example .env  # Add your OpenAI API key
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
