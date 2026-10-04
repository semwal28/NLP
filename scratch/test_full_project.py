import sys
from pathlib import Path
import io
import py_compile

root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

print("=" * 60)
print("COMPREHENSIVE PROJECT INTEGRITY & END-TO-END TEST")
print("=" * 60)

# 1. Syntax & Compilation Check on all Python files
print("\n[1/6] Validating Syntax & Compilation of all Python files...")
py_files = list(root.glob("*.py")) + list((root / "utils").glob("*.py")) + list((root / "prompts").glob("*.py"))
for p in py_files:
    py_compile.compile(str(p), doraise=True)
    print(f"  [OK] {p.name} compiled cleanly")

# 2. Test Demo Data completeness
print("\n[2/6] Validating Demo Data Structures...")
from utils.demo_data import (
    DEMO_PARSED_RESUME,
    DEMO_ATS_RESULT,
    DEMO_SKILL_GAP_RESULT,
    DEMO_INTERVIEW_QUESTIONS,
    DEMO_EVALUATION_RESULT,
)
assert DEMO_PARSED_RESUME.get("name"), "Demo resume missing name"
assert DEMO_ATS_RESULT.get("overall_score") == 88, "Demo ATS score mismatch"
assert len(DEMO_SKILL_GAP_RESULT.get("matched_skills", [])) > 0, "Demo matched skills empty"
assert len(DEMO_INTERVIEW_QUESTIONS.get("questions", [])) == 5, "Demo questions count mismatch"
assert DEMO_EVALUATION_RESULT.get("score") == 9, "Demo evaluation score mismatch"
print("  [OK] All Demo data objects are complete and valid!")

# 3. Test Prompt Template Formatting
print("\n[3/6] Testing Prompt Formatter Templates...")
from prompts.prompts import (
    RESUME_PARSE_PROMPT,
    ATS_SCORE_PROMPT,
    SKILL_GAP_PROMPT,
    INTERVIEW_QUESTIONS_PROMPT,
    ANSWER_EVALUATION_PROMPT,
)
p1 = RESUME_PARSE_PROMPT.format(resume_text="Sample Resume Text")
assert "Sample Resume Text" in p1
p2 = ATS_SCORE_PROMPT.format(resume_text="Sample Resume", job_description="Job Description")
assert "Sample Resume" in p2 and "Job Description" in p2
p3 = SKILL_GAP_PROMPT.format(resume_text="Sample Resume", job_role="Target Role")
assert "Target Role" in p3
p4 = INTERVIEW_QUESTIONS_PROMPT.format(resume_text="Sample Resume", job_role="Target Role", num_questions=3, difficulty="Hard")
assert "3" in p4 and "Hard" in p4
p5 = ANSWER_EVALUATION_PROMPT.format(question="What is Python?", what_to_look_for="Object oriented basics", answer="Python is a dynamic language")
assert "What is Python?" in p5
print("  [OK] All Prompt templates format without errors!")

# 4. Test PDF Extraction logic
print("\n[4/6] Validating PDF Parser Fallback and Safety...")
from utils.resume_parser import extract_text_from_pdf, extract_text_from_docx, parse_resume
# Empty / invalid input checks
assert extract_text_from_pdf(b"") == ""
assert extract_text_from_docx(b"") == ""
assert parse_resume(b"", "resume.pdf") is None
assert parse_resume(b"", "resume.docx") is None
# Non-empty mock PDF header check
assert extract_text_from_pdf(b"%PDF-1.4 mock empty pdf") == ""
print("  [OK] PDF and DOCX parsers gracefully handle corrupt/empty inputs!")

# 5. CSS Classes Sync Check
print("\n[5/6] Verifying CSS Styling and Component Classes...")
import re
with open(root / "app.py", encoding="utf-8") as f:
    app_text = f.read()

with open(root / "assets" / "style.css", encoding="utf-8") as f:
    css_text = f.read()

# Check key CSS classes used in app.py
crucial_classes = [
    "glass-card",
    "gradient-text",
    "stat-card",
    "stat-number",
    "stat-label",
    "tag-matched",
    "tag-missing",
    "tag-skill",
    "tip-card",
    "eval-card",
    "step-card",
    "feature-card",
    "hero-section",
]
for c in crucial_classes:
    assert f".{c}" in css_text, f"Missing CSS class: .{c}"
    print(f"  [OK] CSS class '.{c}' defined")

# 6. Streamlit App Session State and Config Verification
print("\n[6/6] Verifying Config & Environment...")
import config
assert config.APP_TITLE
assert config.SUPPORTED_FILE_TYPES == ["pdf", "docx"]
assert len(config.ATS_SCORE_CATEGORIES) == 5
assert len(config.FALLBACK_MODELS) >= 3
print("  [OK] App configurations match specification!")

print("\n" + "=" * 60)
print("ALL SYSTEM CHECKS & VALIDATIONS PASSED 100% PERFECTLY!")
print("=" * 60)
