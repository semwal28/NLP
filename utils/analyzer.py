"""
Analyzer Module.

Orchestrates the five core NLP analysis features by combining the prompt
templates from ``prompts.prompts`` with the Gemini client.  Each public
function corresponds to one distinct Gemini API call.
"""

from __future__ import annotations

from typing import Any, Optional

from prompts.prompts import (
    RESUME_PARSE_PROMPT,
    ATS_SCORE_PROMPT,
    SKILL_GAP_PROMPT,
    INTERVIEW_QUESTIONS_PROMPT,
    ANSWER_EVALUATION_PROMPT,
)
from utils.gemini_client import call_gemini


# ── API Call 1: Resume Parsing ───────────────────────────────────────────────

def parse_resume_with_ai(resume_text: str) -> Optional[dict[str, Any]]:
    """Send the raw resume text to Gemini for structured parsing.

    Returns:
        A dictionary with keys like ``name``, ``skills``, ``experience``, etc.
    """
    prompt = RESUME_PARSE_PROMPT.format(resume_text=resume_text)
    return call_gemini(prompt)


# ── API Call 2: ATS Scoring ──────────────────────────────────────────────────

def analyse_ats_score(
    resume_text: str,
    job_description: str,
) -> Optional[dict[str, Any]]:
    """Evaluate the resume against a job description for ATS compatibility.

    Returns:
        A dictionary with ``overall_score``, ``category_scores``, and
        ``improvement_suggestions``.
    """
    prompt = ATS_SCORE_PROMPT.format(
        resume_text=resume_text,
        job_description=job_description,
    )
    return call_gemini(prompt)


# ── API Call 3: Skill Gap Analysis ───────────────────────────────────────────

def analyse_skill_gap(
    resume_text: str,
    job_role: str,
) -> Optional[dict[str, Any]]:
    """Compare candidate skills against the target job role requirements.

    Returns:
        A dictionary with ``matched_skills``, ``missing_skills``, and
        ``skill_match_percentage``.
    """
    prompt = SKILL_GAP_PROMPT.format(
        resume_text=resume_text,
        job_role=job_role,
    )
    return call_gemini(prompt)


# ── API Call 4: Interview Question Generation ────────────────────────────────

def generate_interview_questions(
    resume_text: str,
    job_role: str,
    num_questions: int = 5,
    difficulty: str = "Medium",
) -> Optional[dict[str, Any]]:
    """Generate personalised interview questions based on the resume and role.

    Returns:
        A dictionary with a ``questions`` list.
    """
    prompt = INTERVIEW_QUESTIONS_PROMPT.format(
        resume_text=resume_text,
        job_role=job_role,
        num_questions=num_questions,
        difficulty=difficulty,
    )
    return call_gemini(prompt)


# ── API Call 5: Answer Evaluation ────────────────────────────────────────────

def evaluate_answer(
    question: str,
    what_to_look_for: str,
    answer: str,
) -> Optional[dict[str, Any]]:
    """Evaluate the candidate's answer and provide constructive feedback.

    Returns:
        A dictionary with ``score``, ``strengths``, ``improvements``, and
        a ``model_answer``.
    """
    prompt = ANSWER_EVALUATION_PROMPT.format(
        question=question,
        what_to_look_for=what_to_look_for,
        answer=answer,
    )
    return call_gemini(prompt)
