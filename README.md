# 🎯 AI Resume Analyzer & Interview Prep Coach

An NLP-powered web application that leverages **Google Gemini API** to provide intelligent resume analysis, ATS compatibility scoring, skill gap identification, and interactive interview preparation with AI-driven feedback.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.45-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Gemini](https://img.shields.io/badge/Google_Gemini-API-4285F4?style=for-the-badge&logo=google&logoColor=white)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Setup & Installation](#-setup--installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Deployment](#-deployment)
- [LLM Integration Details](#-llm-integration-details)
- [Prompt Engineering](#-prompt-engineering)

---

## ✨ Features

### 1. Smart Resume Parsing
- Upload **PDF** or **DOCX** resume files
- AI-powered extraction of structured data (name, skills, experience, education, projects)
- Clean, tabbed display of parsed information

### 2. ATS Compatibility Scoring
- Evaluate resume against any job description
- Receive a **0-100 ATS score** with detailed category breakdown
- Interactive radar chart visualization
- Matched & missing keyword identification
- Actionable improvement suggestions

### 3. Skill Gap Analysis
- Compare your skills against target job role requirements
- Visual skill match percentage with gauge chart
- Categorized missing skills (Critical / Important / Nice-to-have)
- Personalised learning recommendations for each gap

### 4. AI Mock Interview Generator
- Generate role-specific interview questions (Technical, Behavioral, Situational)
- Configurable difficulty levels (Easy / Medium / Hard)
- Questions are personalised based on your resume content

### 5. Interactive Interview Practice
- Type answers to AI-generated questions
- Receive instant evaluation with **score (1-10)**
- Detailed feedback: strengths, improvements, model answer, and tips
- Session summary with score trend visualization

---

## 🏗️ Architecture

```
User → Streamlit UI → Resume Parser (PyPDF2/python-docx) → Gemini API
                                                              ↓
                                        Structured JSON ← Prompt Templates
                                              ↓
                                     Plotly Visualizations → User
```

The application makes **5 distinct API calls** to Google Gemini:

| # | Purpose | Prompt Template |
|---|---------|----------------|
| 1 | Resume Parsing & Structuring | `RESUME_PARSE_PROMPT` |
| 2 | ATS Score Calculation | `ATS_SCORE_PROMPT` |
| 3 | Skill Gap Analysis | `SKILL_GAP_PROMPT` |
| 4 | Interview Question Generation | `INTERVIEW_QUESTIONS_PROMPT` |
| 5 | Answer Evaluation & Feedback | `ANSWER_EVALUATION_PROMPT` |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Language** | Python 3.10+ |
| **Frontend** | Streamlit with custom CSS |
| **LLM** | Google Gemini 1.5 Flash API |
| **Resume Parsing** | PyPDF2, python-docx |
| **Data Visualization** | Plotly |
| **Config Management** | python-dotenv |

---

## 📁 Project Structure

```
NLP/
├── app.py                    # Main Streamlit application
├── config.py                 # Central configuration (API key resolution, model settings)
├── requirements.txt          # Python dependencies
├── Dockerfile                # Production Docker container configuration
├── .dockerignore             # Docker build ignore rules
├── .env.example              # Environment variable template
├── .gitignore                # Git ignore rules
├── README.md                 # Project documentation
├── .streamlit/
│   ├── config.toml           # Streamlit theme & server configuration
│   └── secrets.toml.example  # Streamlit Cloud secrets template
├── sample_resumes/
│   ├── sample_software_engineer_resume.docx # Pre-loaded sample resume (Alex Morgan)
│   └── sample_job_description.txt           # Sample target job description
├── prompts/
│   ├── __init__.py           # Package initializer
│   └── prompts.py            # All LLM prompt templates (Prompt File)
├── utils/
│   ├── __init__.py           # Package initializer
│   ├── resume_parser.py      # PDF/DOCX text extraction
│   ├── gemini_client.py      # Gemini API wrapper with error handling
│   ├── analyzer.py           # Analysis orchestration (5 API call functions)
│   └── demo_data.py          # Pre-computed realistic data for instant demonstration
└── assets/
    └── style.css             # Custom glassmorphic dark-theme design system
```

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.10 or higher
- A Google Gemini API key (free from [Google AI Studio](https://aistudio.google.com/apikey))

### Step 1: Clone the Repository
```bash
git clone <your-github-repo-url>
cd NLP
```

### Step 2: Create a Virtual Environment (Recommended)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure API Key (3 Flexible Ways)
1. **Via `.env` file** (Recommended for local dev):
   ```bash
   cp .env.example .env
   ```
   Open `.env` and set:
   ```
   GEMINI_API_KEY=AIzaSy...your_actual_key_here
   ```
2. **Via Streamlit Cloud Secrets** (for cloud deployment):
   Add `GEMINI_API_KEY = "AIzaSy..."` in **App Settings → Secrets**.
3. **Directly in the Web UI**:
   You can enter your API key on the fly in the sidebar's **🔑 API Key Settings** or directly in the warning banner without touching any files.

### Step 5: Run the Application
```bash
python -m streamlit run app.py
```
*(or `streamlit run app.py` if `streamlit` is in your PATH)*

The app will automatically open in your browser at `http://localhost:8501`.

### ⚡ 1-Click Demo Mode (No Setup Required)
To evaluate or present the application immediately without an API key:
1. Launch the app (`python -m streamlit run app.py`)
2. In the sidebar, click **"✨ 1-Click Demo Session"**
3. Instantly test and explore:
   - Parsed resume summary with candidate details and 4 categorized tabs
   - Interactive ATS gauge chart, radar chart, keyword pills, and actionable suggestions
   - Skill gap radar and matched vs missing comparative bar charts
   - Mock interview questions with interactive feedback, scoring, and score trendline!

---

## ⚙️ Configuration

All configurable parameters are centralised in [`config.py`](config.py):

```python
GEMINI_MODEL = "gemini-1.5-flash"      # LLM model
MAX_OUTPUT_TOKENS = 8192                # Max response length
TEMPERATURE = 0.7                       # Creativity level
SUPPORTED_FILE_TYPES = ["pdf", "docx"]  # Accepted resume formats
QUESTIONS_PER_SESSION = 5               # Default interview questions
```

---

## 📖 Usage

1. **Upload Resume** — Navigate to "📄 Upload Resume" and upload your PDF/DOCX file
2. **View Parsed Data** — See AI-extracted skills, experience, education, and projects
3. **ATS Analysis** — Go to "📊 ATS Score Analysis", paste a job description, and get your score
4. **Skill Gap** — Go to "🔍 Skill Gap Analysis", enter a target role, and see your gaps
5. **Mock Interview** — Go to "🎤 Mock Interview", configure settings, generate questions, and practice!

---

## 🚀 Deployment

### Deploy to Streamlit Cloud (Recommended)

1. Push your code to a **GitHub repository** (ensure `.env` is in `.gitignore`)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"New app"** → select your repo, branch, and `app.py` as the main file
4. In **Advanced settings → Secrets**, add:
   ```toml
   GEMINI_API_KEY = "your_actual_api_key_here"
   ```
5. Click **Deploy** — your app will be live in ~2 minutes!

### Deploy with Docker (Optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t resume-analyzer .
docker run -p 8501:8501 -e GEMINI_API_KEY=your_key resume-analyzer
```

---

## 🤖 LLM Integration Details

### API Client (`utils/gemini_client.py`)
- Wraps the `google-generativeai` SDK
- Handles JSON response cleaning (strips markdown code fences)
- Provides structured (`call_gemini`) and raw (`call_gemini_raw`) response modes
- Includes comprehensive error handling

### API Key Resolution (`config.py`)
The API key is resolved from multiple sources in priority order:
1. **Streamlit Cloud secrets** (`st.secrets["GEMINI_API_KEY"]`)
2. **Environment variable** (`.env` file or system environment)

This ensures the app works seamlessly both locally and when deployed.

### Prompt Engineering (`prompts/prompts.py`)
Each prompt follows a consistent design pattern:
1. **Role Assignment** — Clear system-level role for the model
2. **Structured Output** — Strict JSON schema with defined keys
3. **Context Injection** — Placeholders for resume text, job descriptions, and answers
4. **Guardrails** — Instructions to return only JSON, be specific, and be actionable

---

## 📄 License

This project is created for educational purposes as part of an NLP course project.

---

## 👤 Author

Built with ❤️ using Google Gemini API and Streamlit.
