"""
Configuration file for AI Resume Analyzer & Interview Prep Coach.

This module centralises every tuneable parameter the application uses,
including model settings, supported file types, scoring categories,
and interview configuration.

The API key is resolved from multiple sources (in priority order):
1. Streamlit Cloud secrets  (``st.secrets["GEMINI_API_KEY"]``)
2. Environment variable     (``.env`` file or system env)
"""

import os
from dotenv import load_dotenv

# ── Load environment variables ───────────────────────────────────────────────
load_dotenv()


def _resolve_api_key() -> str:
    """Resolve the Gemini API key from Streamlit secrets or environment."""
    # 1. Try Streamlit Cloud secrets first
    try:
        import streamlit as st
        key = st.secrets.get("GEMINI_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    # 2. Fall back to .env / system environment
    return os.getenv("GEMINI_API_KEY", "")


# ── Google Gemini API Configuration ──────────────────────────────────────────
GEMINI_API_KEY: str = _resolve_api_key()
GEMINI_MODEL: str = "gemini-3.5-flash-lite"
FALLBACK_MODELS: list[str] = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-flash-latest",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
]
MAX_OUTPUT_TOKENS: int = 8192
TEMPERATURE: float = 0.7
TOP_P: float = 0.95

# ── Resume Upload Settings ───────────────────────────────────────────────────
SUPPORTED_FILE_TYPES: list[str] = ["pdf", "docx"]
MAX_FILE_SIZE_MB: int = 10

# ── ATS Scoring Categories ───────────────────────────────────────────────────
ATS_SCORE_CATEGORIES: list[str] = [
    "Keyword Relevance",
    "Format & Structure",
    "Section Completeness",
    "Impact & Metrics",
    "Overall Readability",
]

# ── Interview Configuration ──────────────────────────────────────────────────
INTERVIEW_DIFFICULTY_LEVELS: list[str] = ["Easy", "Medium", "Hard"]
QUESTIONS_PER_SESSION: int = 5
QUESTION_TYPES: list[str] = ["Technical", "Behavioral", "Situational"]

# ── Application Metadata ────────────────────────────────────────────────────
APP_TITLE: str = "AI Resume Analyzer & Interview Prep Coach"
APP_ICON: str = "🎯"
APP_VERSION: str = "1.0.0"
