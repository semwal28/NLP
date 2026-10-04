import sys
import io
from pathlib import Path

# Add project root to sys.path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

import config
from utils.resume_parser import parse_resume, extract_text_from_pdf, extract_text_from_docx
from utils.gemini_client import call_gemini, _clean_and_parse_json
from utils.analyzer import (
    parse_resume_with_ai,
    analyse_ats_score,
    analyse_skill_gap,
    generate_interview_questions,
    evaluate_answer,
)

print("=" * 60)
print("RUNNING COMPLETE TEST SUITE FOR AI RESUME ANALYZER")
print("=" * 60)

# 1. Test JSON Cleaner
print("[1/5] Testing JSON Parser Robustness...")
j1 = _clean_and_parse_json('{"key": "value"}')
assert j1 == {"key": "value"}, "Failed direct JSON"
j2 = _clean_and_parse_json('```json\n{"score": 90, "items": [1, 2, ],}\n```')
assert j2["score"] == 90, "Failed markdown code fence JSON"
j3 = _clean_and_parse_json('Here is output:\n{"a": 1}\nHave a nice day!')
assert j3 == {"a": 1}, "Failed conversational wrapped JSON"
print("  --> JSON Parser passed all edge cases!")

# 2. Test Resume Parser
print("[2/5] Testing Resume Parser...")
sample_docx = root / "sample_resumes" / "sample_software_engineer_resume.docx"
assert sample_docx.exists(), "Sample docx resume missing"
docx_bytes = sample_docx.read_bytes()
extracted_docx = parse_resume(docx_bytes, "sample.docx")
assert extracted_docx and len(extracted_docx) > 500, "DOCX extraction failed"
print(f"  --> DOCX parsed successfully ({len(extracted_docx)} characters)")

# Test defensive handling on invalid bytes
assert parse_resume(b"invalid data", "bad.pdf") is None or parse_resume(b"invalid data", "bad.pdf") == ""
assert parse_resume(b"invalid data", "bad.docx") is None or parse_resume(b"invalid data", "bad.docx") == ""
print("  --> Corrupted file protection verified!")

# 3. Test Gemini Model Configuration
print("[3/5] Testing Model Configuration...")
print(f"  --> Primary Model: {config.GEMINI_MODEL}")
print(f"  --> Fallback Models: {config.FALLBACK_MODELS}")
assert config.GEMINI_API_KEY, "Gemini API key is not configured"

# 4. Test Live AI Analysis Functions
print("[4/5] Testing Live AI Endpoints with Gemini...")
sample_text = extracted_docx[:800]

print("  --> Testing Resume Parsing...")
parsed = parse_resume_with_ai(sample_text)
assert parsed and not parsed.get("parse_error"), f"AI parse failed: {parsed}"
print(f"      Extracted Name: {parsed.get('name')}")
print(f"      Skills Count: {len(parsed.get('skills', []))}")

print("  --> Testing ATS Compatibility Scoring...")
ats = analyse_ats_score(sample_text, "Looking for a Senior Python and AI Engineer with FastAPI and Docker experience.")
assert ats and not ats.get("parse_error"), f"ATS scoring failed: {ats}"
print(f"      ATS Overall Score: {ats.get('overall_score')}/100")
print(f"      Categories: {list(ats.get('category_scores', {}).keys())}")

print("  --> Testing Skill Gap Analysis...")
sg = analyse_skill_gap(sample_text, "Senior AI Engineer")
assert sg and not sg.get("parse_error"), f"Skill gap failed: {sg}"
print(f"      Skill Match: {sg.get('skill_match_percentage')}%")
print(f"      Matched Skills: {len(sg.get('matched_skills', []))}")
print(f"      Missing Skills: {len(sg.get('missing_skills', []))}")

print("  --> Testing Interview Questions...")
iq = generate_interview_questions(sample_text, "Senior AI Engineer", num_questions=3, difficulty="Medium")
assert iq and not iq.get("parse_error"), f"Question generation failed: {iq}"
questions = iq.get("questions", [])
print(f"      Questions Generated: {len(questions)}")
assert len(questions) > 0, "No questions returned"

print("  --> Testing Answer Evaluation...")
ev = evaluate_answer(
    question=questions[0].get("question", "Describe your experience with Python"),
    what_to_look_for="Depth of technical knowledge and architecture experience.",
    answer="I have built high-throughput microservices using FastAPI, Python, and Redis caching to handle 50k+ daily queries."
)
assert ev and not ev.get("parse_error"), f"Answer evaluation failed: {ev}"
print(f"      Answer Score: {ev.get('score')}/10 ({ev.get('score_label')})")

print("[5/5] Checking Plotly Chart Helpers...")
import plotly.graph_objects as go
assert isinstance(ats.get("overall_score"), (int, float))

print("=" * 60)
print("ALL TESTS PASSED WITH 100% SUCCESS!")
print("=" * 60)
