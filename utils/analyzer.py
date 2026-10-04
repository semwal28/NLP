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


import re


# ── Helper for numeric normalization ──────────────────────────────────────────

def _extract_int(val: Any, default: int = 0) -> int:
    """Safely convert strings or numbers into integers."""
    if isinstance(val, (int, float)):
        return int(val)
    if isinstance(val, str):
        digits = re.findall(r"\d+", val)
        if digits:
            return int(digits[0])
    return default


# ── API Call 1: Resume Parsing ───────────────────────────────────────────────

def parse_resume_with_ai(resume_text: str) -> Optional[dict[str, Any]]:
    """Send the raw resume text to Gemini for structured parsing.

    Returns:
        A dictionary with keys like ``name``, ``skills``, ``experience``, etc.
    """
    prompt = RESUME_PARSE_PROMPT.format(resume_text=resume_text)
    res = call_gemini(prompt)
    if not res or res.get("parse_error"):
        return res

    # Ensure required fields have valid defaults
    res.setdefault("name", "Candidate")
    res.setdefault("skills", [])
    res.setdefault("experience", [])
    res.setdefault("education", [])
    res.setdefault("projects", [])
    return res


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
    res = call_gemini(prompt)
    if not res or res.get("parse_error"):
        return res

    res["overall_score"] = _extract_int(res.get("overall_score"), 70)
    cat_scores = res.get("category_scores")
    if isinstance(cat_scores, dict):
        for k, v in cat_scores.items():
            if isinstance(v, dict):
                v["score"] = _extract_int(v.get("score"), 70)
            elif isinstance(v, (int, float, str)):
                cat_scores[k] = {"score": _extract_int(v, 70), "feedback": ""}
    else:
        res["category_scores"] = {}

    res.setdefault("matched_keywords", [])
    res.setdefault("missing_keywords", [])
    res.setdefault("improvement_suggestions", [])
    return res


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
    res = call_gemini(prompt)
    if not res or res.get("parse_error"):
        return res

    res["skill_match_percentage"] = _extract_int(res.get("skill_match_percentage"), 70)

    # Normalize matched_skills
    raw_matched = res.get("matched_skills", [])
    normalized_matched = []
    if isinstance(raw_matched, list):
        for item in raw_matched:
            if isinstance(item, dict):
                normalized_matched.append(item)
            elif isinstance(item, str):
                normalized_matched.append({
                    "skill": item,
                    "proficiency": "Moderate",
                    "evidence": "Demonstrated in resume",
                })
    res["matched_skills"] = normalized_matched

    # Normalize missing_skills
    raw_missing = res.get("missing_skills", [])
    normalized_missing = []
    if isinstance(raw_missing, list):
        for item in raw_missing:
            if isinstance(item, dict):
                normalized_missing.append(item)
            elif isinstance(item, str):
                normalized_missing.append({
                    "skill": item,
                    "importance": "Important",
                    "recommendation": f"Complete hands-on projects or certifications in {item}.",
                })
    res["missing_skills"] = normalized_missing

    return res


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
    res = call_gemini(prompt)
    if not res or res.get("parse_error"):
        return res

    # If the response returned list directly or wrapped in data/items
    questions = []
    if isinstance(res, list):
        questions = res
    elif isinstance(res, dict):
        if "questions" in res and isinstance(res["questions"], list):
            questions = res["questions"]
        elif "items" in res and isinstance(res["items"], list):
            questions = res["items"]
        elif "data" in res and isinstance(res["data"], list):
            questions = res["data"]

    # Ensure each question has standard fields
    clean_questions = []
    for idx, q in enumerate(questions, start=1):
        if isinstance(q, dict):
            clean_questions.append({
                "id": q.get("id", idx),
                "question": q.get("question", f"Question {idx}"),
                "type": q.get("type", "Technical"),
                "difficulty": q.get("difficulty", difficulty),
                "what_to_look_for": q.get("what_to_look_for", ""),
                "related_skill": q.get("related_skill", "General"),
            })
        elif isinstance(q, str):
            clean_questions.append({
                "id": idx,
                "question": q,
                "type": "Technical",
                "difficulty": difficulty,
                "what_to_look_for": "Clear structured explanation.",
                "related_skill": "General",
            })

    return {"questions": clean_questions}


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
    res = call_gemini(prompt)
    if not res or res.get("parse_error"):
        return res

    raw_score = _extract_int(res.get("score"), 7)
    res["score"] = max(1, min(10, raw_score))
    if not res.get("score_label"):
        if res["score"] >= 8:
            res["score_label"] = "Excellent"
        elif res["score"] >= 6:
            res["score_label"] = "Good"
        elif res["score"] >= 4:
            res["score_label"] = "Average"
        else:
            res["score_label"] = "Needs Improvement"

    res.setdefault("strengths", [])
    res.setdefault("improvements", [])
    res.setdefault("tips", [])
    return res
