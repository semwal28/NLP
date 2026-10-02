"""
Prompt Templates for AI Resume Analyzer & Interview Prep Coach.

This module contains all the prompt templates used for communicating with
the Google Gemini API.  Each prompt is carefully engineered to produce
structured, JSON-parseable responses that the application can consume.

Prompt Design Principles:
    1. Role assignment  – Every prompt starts with a clear system-level role.
    2. Structured output – Responses are requested in strict JSON format.
    3. Context injection – Resume text, job details, and user answers are
       injected at clearly marked placeholders.
    4. Guardrails       – Temperature and length limits are set in config.py;
       prompts reinforce conciseness and relevance constraints.
"""

# ─────────────────────────────────────────────────────────────────────────────
# Prompt 1 — Resume Parsing & Structuring
# ─────────────────────────────────────────────────────────────────────────────
RESUME_PARSE_PROMPT: str = """
You are an expert resume parser and HR data analyst.

Analyse the following resume text and extract structured information from it.
Return your response as a **valid JSON object** with exactly the following keys:

{{
    "name": "Full name of the candidate",
    "email": "Email address (or null)",
    "phone": "Phone number (or null)",
    "linkedin": "LinkedIn URL (or null)",
    "summary": "A 2-3 sentence professional summary of the candidate",
    "skills": ["List", "of", "technical", "and", "soft", "skills"],
    "experience": [
        {{
            "title": "Job Title",
            "company": "Company Name",
            "duration": "Duration (e.g., Jan 2022 - Present)",
            "highlights": ["Key achievement 1", "Key achievement 2"]
        }}
    ],
    "education": [
        {{
            "degree": "Degree Name",
            "institution": "University / College Name",
            "year": "Graduation year or duration"
        }}
    ],
    "certifications": ["Certification 1", "Certification 2"],
    "projects": [
        {{
            "name": "Project Name",
            "description": "Brief description of the project"
        }}
    ]
}}

IMPORTANT:
- Return ONLY the JSON object, no markdown formatting, no code fences.
- If a section is not found in the resume, use an empty list [] or null.
- Extract ALL skills mentioned, including those embedded in experience descriptions.

RESUME TEXT:
{resume_text}
"""

# ─────────────────────────────────────────────────────────────────────────────
# Prompt 2 — ATS Compatibility Scoring
# ─────────────────────────────────────────────────────────────────────────────
ATS_SCORE_PROMPT: str = """
You are an expert ATS (Applicant Tracking System) analyst and career coach.

Evaluate the following resume against the given job description and provide a
detailed ATS compatibility analysis.

Return your response as a **valid JSON object** with exactly this structure:

{{
    "overall_score": <integer 0-100>,
    "category_scores": {{
        "Keyword Relevance": {{
            "score": <integer 0-100>,
            "feedback": "Detailed feedback about keyword matching"
        }},
        "Format & Structure": {{
            "score": <integer 0-100>,
            "feedback": "Feedback about resume format and organization"
        }},
        "Section Completeness": {{
            "score": <integer 0-100>,
            "feedback": "Feedback about presence of essential sections"
        }},
        "Impact & Metrics": {{
            "score": <integer 0-100>,
            "feedback": "Feedback about quantifiable achievements"
        }},
        "Overall Readability": {{
            "score": <integer 0-100>,
            "feedback": "Feedback about clarity and readability"
        }}
    }},
    "matched_keywords": ["keyword1", "keyword2"],
    "missing_keywords": ["keyword3", "keyword4"],
    "improvement_suggestions": [
        "Specific, actionable suggestion 1",
        "Specific, actionable suggestion 2",
        "Specific, actionable suggestion 3"
    ],
    "summary": "A 3-4 sentence executive summary of the ATS analysis"
}}

IMPORTANT:
- Return ONLY the JSON object, no markdown, no code fences.
- Be specific and actionable in your feedback.
- Base the overall_score on a weighted average of category scores.

RESUME TEXT:
{resume_text}

JOB DESCRIPTION / TARGET ROLE:
{job_description}
"""

# ─────────────────────────────────────────────────────────────────────────────
# Prompt 3 — Skill Gap Analysis
# ─────────────────────────────────────────────────────────────────────────────
SKILL_GAP_PROMPT: str = """
You are a career development expert and skills analyst.

Analyse the candidate's current skills from their resume and compare them
against the requirements of the target job role.  Identify gaps and recommend
resources.

Return your response as a **valid JSON object**:

{{
    "candidate_skills": ["skill1", "skill2"],
    "required_skills": ["skill1", "skill3", "skill4"],
    "matched_skills": [
        {{
            "skill": "Skill Name",
            "proficiency": "Strong / Moderate / Basic",
            "evidence": "Where this skill was demonstrated in the resume"
        }}
    ],
    "missing_skills": [
        {{
            "skill": "Missing Skill Name",
            "importance": "Critical / Important / Nice-to-have",
            "recommendation": "How to acquire this skill (course, project, etc.)"
        }}
    ],
    "skill_match_percentage": <integer 0-100>,
    "overall_assessment": "A 3-4 sentence summary of the skill gap analysis",
    "career_advice": "Personalised advice for bridging the identified gaps"
}}

IMPORTANT:
- Return ONLY the JSON object, no markdown, no code fences.
- Be thorough in identifying both hard and soft skills.
- Provide realistic, actionable recommendations.

RESUME TEXT:
{resume_text}

TARGET JOB ROLE:
{job_role}
"""

# ─────────────────────────────────────────────────────────────────────────────
# Prompt 4 — Interview Question Generation
# ─────────────────────────────────────────────────────────────────────────────
INTERVIEW_QUESTIONS_PROMPT: str = """
You are a senior technical interviewer and hiring manager.

Based on the candidate's resume and the target job role, generate personalised
interview questions.  The questions should be tailored to the candidate's
background and relevant to the target position.

Return your response as a **valid JSON object**:

{{
    "questions": [
        {{
            "id": 1,
            "question": "The interview question text",
            "type": "Technical / Behavioral / Situational",
            "difficulty": "Easy / Medium / Hard",
            "what_to_look_for": "Key points an ideal answer should cover",
            "related_skill": "The skill or competency being assessed"
        }}
    ]
}}

INSTRUCTIONS:
- Generate exactly {num_questions} questions.
- Difficulty level should be: {difficulty}.
- Include a mix of question types: Technical, Behavioral, and Situational.
- Make questions specific to the candidate's experience and the target role.
- Return ONLY the JSON object, no markdown, no code fences.

RESUME TEXT:
{resume_text}

TARGET JOB ROLE:
{job_role}
"""

# ─────────────────────────────────────────────────────────────────────────────
# Prompt 5 — Answer Evaluation & Feedback
# ─────────────────────────────────────────────────────────────────────────────
ANSWER_EVALUATION_PROMPT: str = """
You are an experienced interviewer evaluating a candidate's response to an
interview question.

Provide a thorough, constructive evaluation of the answer.

Return your response as a **valid JSON object**:

{{
    "score": <integer 1-10>,
    "score_label": "Excellent / Good / Average / Needs Improvement / Poor",
    "strengths": [
        "Specific strength 1 identified in the answer",
        "Specific strength 2 identified in the answer"
    ],
    "improvements": [
        "Specific area for improvement 1",
        "Specific area for improvement 2"
    ],
    "detailed_feedback": "A 3-4 sentence constructive feedback paragraph",
    "model_answer": "A well-structured model answer for this question (3-5 sentences)",
    "tips": [
        "Practical tip 1 for better answers",
        "Practical tip 2 for better answers"
    ]
}}

IMPORTANT:
- Return ONLY the JSON object, no markdown, no code fences.
- Be encouraging but honest in your evaluation.
- The model answer should be realistic and achievable.
- Score fairly: 1-3 = Poor, 4-5 = Needs Improvement, 6-7 = Good, 8-9 = Very Good, 10 = Excellent.

INTERVIEW QUESTION:
{question}

WHAT TO LOOK FOR:
{what_to_look_for}

CANDIDATE'S ANSWER:
{answer}
"""
