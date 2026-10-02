"""
AI Resume Analyzer & Interview Prep Coach — Main Application.

A Streamlit-based NLP application that integrates Google Gemini API
to provide intelligent resume analysis, ATS scoring, skill gap
identification, and interactive interview preparation.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

import config
from utils.resume_parser import parse_resume
from utils.analyzer import (
    parse_resume_with_ai,
    analyse_ats_score,
    analyse_skill_gap,
    generate_interview_questions,
    evaluate_answer,
)
from utils.demo_data import (
    DEMO_PARSED_RESUME,
    DEMO_ATS_RESULT,
    DEMO_SKILL_GAP_RESULT,
    DEMO_INTERVIEW_QUESTIONS,
    DEMO_EVALUATION_RESULT,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Page Configuration
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load Custom CSS ───────────────────────────────────────────────────────────
css_path = Path(__file__).parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Session State Initialisation
# ═══════════════════════════════════════════════════════════════════════════════

_defaults: dict = {
    "resume_text": None,
    "resume_filename": None,
    "parsed_resume": None,
    "ats_result": None,
    "skill_gap_result": None,
    "interview_questions": None,
    "current_question_idx": 0,
    "interview_scores": [],
    "evaluation_results": {},
    "custom_api_key": "",
    "target_jd_input": "",
    "target_role_input": "",
    "target_interview_role": "",
}
for key, val in _defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ═══════════════════════════════════════════════════════════════════════════════
# Helper Functions & Utilities
# ═══════════════════════════════════════════════════════════════════════════════

def _get_active_api_key() -> str:
    """Retrieve active API key from session state, config, or secrets."""
    if st.session_state.get("custom_api_key"):
        return st.session_state["custom_api_key"]
    key = config.GEMINI_API_KEY
    if key and key != "your_gemini_api_key_here":
        return key
    return ""


def _api_key_configured() -> bool:
    """Check whether a real API key has been set."""
    key = _get_active_api_key()
    return bool(key and len(key) > 10)


def _sync_api_key() -> None:
    """Ensure config.GEMINI_API_KEY is updated with active key."""
    active_key = _get_active_api_key()
    if active_key:
        config.GEMINI_API_KEY = active_key


def _show_api_warning() -> None:
    """Render a prominent banner when the API key is missing."""
    st.markdown(
        """
        <div class="api-warning">
            ⚠️ <strong>Gemini API key not configured.</strong>
            Please configure your key in <code>.env</code>, enter it below for this session,
            or click <strong>⚡ 1-Click Demo Session</strong> in the sidebar to test immediately.
            Get a free key from
            <a href="https://aistudio.google.com/apikey" target="_blank" style="color:#00D4AA; font-weight:600;">
            Google AI Studio</a>.
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("🔑 Enter Gemini API Key for this Session", expanded=False):
        col_k1, col_k2 = st.columns([3, 1])
        with col_k1:
            entered_key = st.text_input(
                "Gemini API Key",
                type="password",
                placeholder="AIzaSy...",
                key="inline_api_key_input",
                label_visibility="collapsed",
            )
        with col_k2:
            if st.button("Save Key", key="save_inline_key", use_container_width=True):
                if entered_key.strip():
                    st.session_state.custom_api_key = entered_key.strip()
                    _sync_api_key()
                    st.success("API Key saved!")
                    st.rerun()


def _score_color(score: int | float) -> str:
    """Return a hex colour code appropriate for score (0-100)."""
    if score >= 80:
        return "#10B981"
    elif score >= 60:
        return "#00D4AA"
    elif score >= 40:
        return "#F59E0B"
    return "#EF4444"


def _score_label(score: int | float) -> str:
    if score >= 80:
        return "Excellent"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Average"
    return "Needs Improvement"


def _build_gauge(score: int | float, title: str = "Score") -> go.Figure:
    """Create a Plotly gauge chart for a 0-100 score."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": title, "font": {"size": 16, "color": "#E8E8ED", "family": "Inter"}},
            number={"font": {"size": 48, "color": _score_color(score), "family": "Inter"}, "suffix": "/100"},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#2D3148"},
                "bar": {"color": _score_color(score), "thickness": 0.7},
                "bgcolor": "#1A1D2E",
                "borderwidth": 1,
                "bordercolor": "#2D3148",
                "steps": [
                    {"range": [0, 40], "color": "rgba(239,68,68,0.1)"},
                    {"range": [40, 60], "color": "rgba(245,158,11,0.1)"},
                    {"range": [60, 80], "color": "rgba(0,212,170,0.1)"},
                    {"range": [80, 100], "color": "rgba(16,185,129,0.1)"},
                ],
                "threshold": {
                    "line": {"color": "#6C63FF", "width": 3},
                    "thickness": 0.8,
                    "value": score,
                },
            },
        )
    )
    fig.update_layout(
        height=260,
        margin=dict(l=30, r=30, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#E8E8ED", "family": "Inter"},
    )
    return fig


def _build_radar(categories: list[str], scores: list[int | float]) -> go.Figure:
    """Create a radar chart for multi-dimensional scores."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=scores + [scores[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor="rgba(108,99,255,0.15)",
            line={"color": "#6C63FF", "width": 2},
            marker={"size": 6, "color": "#00D4AA"},
            name="Score",
        )
    )
    fig.update_layout(
        polar={
            "bgcolor": "rgba(0,0,0,0)",
            "radialaxis": {
                "visible": True,
                "range": [0, 100],
                "gridcolor": "#2D3148",
                "tickfont": {"color": "#9CA3AF", "size": 10},
            },
            "angularaxis": {
                "gridcolor": "#2D3148",
                "tickfont": {"color": "#E8E8ED", "size": 11, "family": "Inter"},
            },
        },
        showlegend=False,
        height=380,
        margin=dict(l=60, r=60, t=40, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#E8E8ED", "family": "Inter"},
    )
    return fig


def _build_skill_bars(matched: list[dict], missing: list[dict]) -> go.Figure:
    """Create a horizontal bar chart comparing matched vs missing skills."""
    all_skills = []
    colors = []
    categories = []

    for item in matched:
        all_skills.append(item.get("skill", "Unknown"))
        colors.append("#10B981")
        categories.append("Matched")

    for item in missing:
        all_skills.append(item.get("skill", "Unknown"))
        colors.append("#EF4444")
        categories.append("Missing")

    fig = go.Figure()
    if all_skills:
        fig.add_trace(
            go.Bar(
                y=all_skills,
                x=[1] * len(all_skills),
                orientation="h",
                marker={"color": colors, "line": {"width": 0}},
                text=categories,
                textposition="inside",
                textfont={"color": "white", "size": 12, "family": "Inter"},
                hovertemplate="%{y}: %{text}<extra></extra>",
            )
        )
    fig.update_layout(
        height=max(300, len(all_skills) * 36),
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis={"visible": False},
        yaxis={
            "autorange": "reversed",
            "tickfont": {"color": "#E8E8ED", "size": 12, "family": "Inter"},
            "gridcolor": "rgba(0,0,0,0)",
        },
        font={"color": "#E8E8ED", "family": "Inter"},
        bargap=0.3,
    )
    return fig


def _render_parsed_resume_view(parsed: dict) -> None:
    """Render structured parsed resume summary with tabs and metrics."""
    st.markdown("### 📋 Parsed Resume Overview")

    info_cols = st.columns(3)
    info_cols[0].metric("👤 Name", parsed.get("name") or "N/A")
    info_cols[1].metric("📧 Email", parsed.get("email") or "N/A")
    info_cols[2].metric("📱 Phone", parsed.get("phone") or "N/A")

    st.markdown("<br>", unsafe_allow_html=True)

    if parsed.get("summary"):
        st.markdown(
            f"""
            <div class="glass-card fade-in">
                <h4 style="color:#8B83FF; margin-bottom:8px;">💡 Professional Summary</h4>
                <p style="color:#E8E8ED; line-height:1.6; margin:0;">{parsed["summary"]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(
        ["💼 Experience", "🎓 Education", "🛠️ Skills", "📂 Projects"]
    )

    with tab1:
        experiences = parsed.get("experience", [])
        if experiences:
            for exp in experiences:
                with st.expander(f"**{exp.get('title', 'Role')}** — {exp.get('company', 'Company')}", expanded=True):
                    st.caption(exp.get("duration", ""))
                    for hl in exp.get("highlights", []):
                        st.markdown(f"- {hl}")
        else:
            st.info("No work experience found in the resume.")

    with tab2:
        education = parsed.get("education", [])
        if education:
            for edu in education:
                st.markdown(
                    f"🎓 **{edu.get('degree', 'Degree')}** — {edu.get('institution', '')} "
                    f"({edu.get('year', '')})"
                )
        else:
            st.info("No education information found.")

    with tab3:
        skills = parsed.get("skills", [])
        if skills:
            skill_html = " ".join(f'<span class="tag-skill">{s}</span>' for s in skills)
            st.markdown(skill_html, unsafe_allow_html=True)
        else:
            st.info("No skills extracted.")

    with tab4:
        projects = parsed.get("projects", [])
        if projects:
            for proj in projects:
                st.markdown(f"**{proj.get('name', 'Project')}**")
                st.markdown(f"> {proj.get('description', '')}")
                st.markdown("---")
        else:
            st.info("No projects found in the resume.")


def _render_footer() -> None:
    """Render the application footer."""
    st.markdown(
        f"""
        <div class="app-footer">
            <p>
                <strong>AI Resume Analyzer & Interview Prep Coach</strong>
                v{config.APP_VERSION}
            </p>
            <p>
                Powered by <a href="https://deepmind.google/technologies/gemini/"
                target="_blank">Google Gemini</a> •
                Built with <a href="https://streamlit.io" target="_blank">Streamlit</a>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Sidebar Navigation & Settings
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding:10px 0 16px 0;">
            <span style="font-size:2.8rem;">🎯</span>
            <h2 class="gradient-text" style="margin:4px 0 0 0; font-size:1.3rem;">
                AI Resume Analyzer
            </h2>
            <p style="color:#9CA3AF; font-size:0.82rem; margin-top:4px;">
                Interview Prep Coach
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🏠  Home",
            "📄  Upload Resume",
            "📊  ATS Score Analysis",
            "🔍  Skill Gap Analysis",
            "🎤  Mock Interview",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    # Active Resume Status
    if st.session_state.resume_text:
        fname = st.session_state.get("resume_filename", "Resume Loaded")
        chars = len(st.session_state.resume_text)
        st.markdown(
            f"""
            <div style="background:rgba(16,185,129,0.1); border:1px solid #10B981; border-radius:8px; padding:10px; margin-bottom:8px;">
                <div style="color:#10B981; font-weight:600; font-size:0.85rem;">✅ Active Resume</div>
                <div style="color:#E8E8ED; font-size:0.82rem; word-break:break-all; font-weight:500;">{fname}</div>
                <div style="color:#9CA3AF; font-size:0.75rem;">{chars:,} chars</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🗑️ Clear Active Resume", use_container_width=True):
            st.session_state.resume_text = None
            st.session_state.resume_filename = None
            st.session_state.parsed_resume = None
            st.rerun()
    else:
        st.caption("📄 No resume uploaded yet")

    # 1-Click Demo Loader
    st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
    if st.button("✨ 1-Click Demo Session", use_container_width=True, help="Load pre-computed sample resume, ATS score, skill gap, and interview questions"):
        sample_path = Path(__file__).parent / "sample_resumes" / "sample_software_engineer_resume.docx"
        if sample_path.exists():
            data = sample_path.read_bytes()
            st.session_state.resume_text = parse_resume(data, "sample_software_engineer_resume.docx")
        st.session_state.resume_filename = "Alex Morgan - Senior AI Engineer (Sample)"
        st.session_state.parsed_resume = DEMO_PARSED_RESUME
        st.session_state.ats_result = DEMO_ATS_RESULT
        st.session_state.skill_gap_result = DEMO_SKILL_GAP_RESULT
        st.session_state.interview_questions = DEMO_INTERVIEW_QUESTIONS["questions"]
        st.session_state.evaluation_results = {0: DEMO_EVALUATION_RESULT}
        st.session_state.interview_scores = [9]
        sample_jd_path = Path(__file__).parent / "sample_resumes" / "sample_job_description.txt"
        if sample_jd_path.exists():
            st.session_state.target_jd_input = sample_jd_path.read_text(encoding="utf-8")
        st.session_state.target_role_input = "Senior Full Stack / AI Engineer"
        st.session_state.target_interview_role = "Senior Full Stack / AI Engineer"
        st.success("Demo session loaded!")
        st.rerun()

    # Reset Data
    if st.session_state.ats_result or st.session_state.skill_gap_result or st.session_state.interview_questions:
        if st.button("🔄 Reset All Analyses", use_container_width=True):
            st.session_state.ats_result = None
            st.session_state.skill_gap_result = None
            st.session_state.interview_questions = None
            st.session_state.evaluation_results = {}
            st.session_state.interview_scores = []
            st.rerun()

    st.divider()

    # API Key Configuration
    with st.expander("🔑 API Key Settings", expanded=not _api_key_configured()):
        current_configured = _api_key_configured()
        if current_configured:
            st.markdown("<span style='color:#10B981; font-size:0.85rem;'>● API Key Active</span>", unsafe_allow_html=True)
            st.caption("Active key loaded from " + ("Session input" if st.session_state.get("custom_api_key") else "Environment / Secrets"))
        else:
            st.markdown("<span style='color:#EF4444; font-size:0.85rem;'>● Missing Key</span>", unsafe_allow_html=True)
            st.caption("Add key below or in `.env`")

        sidebar_key = st.text_input(
            "Change / Set Key",
            type="password",
            placeholder="AIzaSy...",
            key="sidebar_key_field",
        )
        if st.button("Update Key", key="btn_update_sidebar_key", use_container_width=True):
            if sidebar_key.strip():
                st.session_state.custom_api_key = sidebar_key.strip()
                _sync_api_key()
                st.success("API Key updated!")
                st.rerun()

    st.caption(f"v{config.APP_VERSION} • Google Gemini 1.5")


# ═══════════════════════════════════════════════════════════════════════════════
# Page: Home
# ═══════════════════════════════════════════════════════════════════════════════

if page == "🏠  Home":

    # API key check
    if not _api_key_configured():
        _show_api_warning()

    # Hero section
    st.markdown(
        """
        <div class="hero-section fade-in">
            <div class="hero-badge">✨ Powered by Google Gemini AI</div>
            <h1 class="gradient-text" style="font-size:2.8rem; margin-bottom:8px;">
                AI Resume Analyzer &<br>Interview Prep Coach
            </h1>
            <p class="hero-subtitle">
                Upload your resume, get an instant ATS compatibility score,
                identify skill gaps, and practice with AI-generated interview
                questions — all powered by <strong style="color:#8B83FF;">Google Gemini</strong>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick Stats Row
    s1, s2, s3, s4 = st.columns(4)
    stat_items = [
        ("95%+", "Parsing Accuracy", "Extracts complex technical resumes"),
        ("5 Categories", "ATS Breakdown", "Granular scoring across key criteria"),
        ("Tailored", "Skill Gap Map", "Actionable courses & recommendations"),
        ("Real-time", "Interview Coach", "Instant scoring & ideal model answers"),
    ]
    for col, (num, label, desc) in zip([s1, s2, s3, s4], stat_items):
        with col:
            st.markdown(
                f"""
                <div class="stat-card fade-in">
                    <div class="stat-number">{num}</div>
                    <div class="stat-label">{label}</div>
                    <p style="color:#6B7280; font-size:0.8rem; margin-top:4px;">{desc}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature cards
    cols = st.columns(4)
    features = [
        ("📄", "Smart Resume Parsing", "AI-powered extraction of skills, experience, and education from your resume."),
        ("📊", "ATS Score Analysis", "Get a detailed ATS compatibility score with actionable improvement tips."),
        ("🔍", "Skill Gap Finder", "Identify missing skills and get personalised learning recommendations."),
        ("🎤", "Mock Interviews", "Practice with AI-generated questions and receive instant feedback."),
    ]
    for col, (icon, title, desc) in zip(cols, features):
        with col:
            st.markdown(
                f"""
                <div class="feature-card fade-in">
                    <div class="feature-icon">{icon}</div>
                    <div class="feature-title">{title}</div>
                    <div class="feature-desc">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # How-it-works section
    st.markdown(
        """
        <div style="text-align:center; margin-top:16px;">
            <h3 style="color:#E8E8ED;">How It Works</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    steps = st.columns(3)
    step_data = [
        ("1️⃣", "Upload Your Resume", "Upload a PDF or DOCX file of your resume, or click Load Sample."),
        ("2️⃣", "Choose Analysis Type", "Select ATS Scoring, Skill Gap, or Mock Interview from the sidebar."),
        ("3️⃣", "Get AI Insights", "Receive detailed, actionable feedback, charts, and model answers."),
    ]
    for col, (num, title, desc) in zip(steps, step_data):
        with col:
            st.markdown(
                f"""
                <div class="step-card fade-in">
                    <div class="step-number">{num}</div>
                    <div class="step-title">{title}</div>
                    <div class="step-desc">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    _render_footer()


# ═══════════════════════════════════════════════════════════════════════════════
# Page: Upload Resume
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "📄  Upload Resume":
    st.markdown(
        '<h2 class="gradient-text">📄 Upload Your Resume</h2>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="color:#9CA3AF;">Upload a PDF or DOCX resume to get started with AI-powered analysis, or load our pre-configured sample profile.</p>',
        unsafe_allow_html=True,
    )

    if not _api_key_configured():
        _show_api_warning()

    st.markdown("<br>", unsafe_allow_html=True)

    # Active Resume Bar
    if st.session_state.resume_text:
        fname = st.session_state.get("resume_filename", "Uploaded Resume")
        chars = len(st.session_state.resume_text)
        col_act1, col_act2, col_act3 = st.columns([3, 1, 1])
        with col_act1:
            st.markdown(
                f"""
                <div style="background:rgba(16,185,129,0.1); border:1px solid #10B981; border-radius:10px; padding:12px 18px;">
                    <span style="color:#10B981; font-weight:600; font-size:1.05rem;">✅ Active Resume:</span>
                    <strong style="color:#E8E8ED; margin-left:8px;">{fname}</strong>
                    <span style="color:#9CA3AF; font-size:0.85rem; margin-left:12px;">({chars:,} characters)</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_act2:
            if st.session_state.parsed_resume:
                st.download_button(
                    "📥 Export JSON",
                    data=json.dumps(st.session_state.parsed_resume, indent=2),
                    file_name="parsed_resume.json",
                    mime="application/json",
                    use_container_width=True,
                )
        with col_act3:
            if st.button("🗑️ Clear", use_container_width=True, help="Clear active resume and upload a new one"):
                st.session_state.resume_text = None
                st.session_state.parsed_resume = None
                st.session_state.resume_filename = None
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

    # Upload options if not yet uploaded
    if not st.session_state.resume_text:
        col_up, col_or, col_sample = st.columns([5, 1, 4])
        with col_up:
            st.markdown("#### Option A: Upload Resume File")
            uploaded = st.file_uploader(
                "Choose your resume file",
                type=config.SUPPORTED_FILE_TYPES,
                help="Supported formats: PDF, DOCX (Max 10 MB)",
                label_visibility="collapsed",
            )
            if uploaded is not None:
                file_bytes = uploaded.read()
                resume_text = parse_resume(file_bytes, uploaded.name)
                if resume_text and resume_text.strip():
                    st.session_state.resume_text = resume_text
                    st.session_state.resume_filename = uploaded.name
                    if _api_key_configured():
                        with st.spinner("🧠 Analysing resume with Gemini AI..."):
                            _sync_api_key()
                            parsed = parse_resume_with_ai(resume_text)
                            if parsed and not parsed.get("parse_error"):
                                st.session_state.parsed_resume = parsed
                    st.rerun()
                else:
                    st.error("❌ Could not extract text from file. Please ensure it is not a scanned image PDF.")

        with col_or:
            st.markdown(
                '<div style="text-align:center; padding-top:40px; color:#6B7280; font-weight:700;">OR</div>',
                unsafe_allow_html=True,
            )

        with col_sample:
            st.markdown("#### Option B: Load Demo Resume")
            st.markdown(
                """
                <div class="glass-card" style="padding:16px;">
                    <div style="font-weight:600; color:#E8E8ED; margin-bottom:4px;">Alex Morgan (Senior AI & Full Stack Engineer)</div>
                    <div style="font-size:0.85rem; color:#9CA3AF; margin-bottom:12px;">5+ YOE in Python, FastAPI, React, LLMs, AWS & Docker. Ready for 1-click testing.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("✨ Load Sample Resume", use_container_width=True):
                sample_file = Path(__file__).parent / "sample_resumes" / "sample_software_engineer_resume.docx"
                if sample_file.exists():
                    data = sample_file.read_bytes()
                    st.session_state.resume_text = parse_resume(data, "sample_software_engineer_resume.docx")
                st.session_state.resume_filename = "Alex Morgan - Senior AI Engineer (Sample)"
                st.session_state.parsed_resume = DEMO_PARSED_RESUME
                st.success("Sample resume loaded successfully!")
                st.rerun()

    # Display Parsed Resume View
    if st.session_state.parsed_resume:
        _render_parsed_resume_view(st.session_state.parsed_resume)
    elif st.session_state.resume_text:
        st.info("ℹ️ Raw resume text extracted successfully. Click below to run AI parsing.")
        if st.button("🧠 Parse with Gemini AI", use_container_width=True):
            if not _api_key_configured():
                st.session_state.parsed_resume = DEMO_PARSED_RESUME
                st.rerun()
            else:
                with st.spinner("🧠 Analysing resume with Gemini AI..."):
                    _sync_api_key()
                    parsed = parse_resume_with_ai(st.session_state.resume_text)
                    if parsed and not parsed.get("parse_error"):
                        st.session_state.parsed_resume = parsed
                        st.rerun()
                    else:
                        st.error("Failed to parse resume with AI.")

    _render_footer()


# ═══════════════════════════════════════════════════════════════════════════════
# Page: ATS Score Analysis
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "📊  ATS Score Analysis":
    st.markdown(
        '<h2 class="gradient-text">📊 ATS Compatibility Score</h2>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="color:#9CA3AF;">See how well your resume matches the target job description for Applicant Tracking Systems.</p>',
        unsafe_allow_html=True,
    )

    if not _api_key_configured():
        _show_api_warning()

    if not st.session_state.resume_text:
        st.warning("⚠️ Please upload your resume first from the **📄 Upload Resume** page, or click **✨ 1-Click Demo Session** in the sidebar.")
    else:
        col_jd_top1, col_jd_top2 = st.columns([3, 1])
        with col_jd_top1:
            st.markdown("#### Job Description / Target Role")
        with col_jd_top2:
            if st.button("📋 Insert Sample JD", help="Load TechNova Senior Full Stack / AI Engineer job description"):
                sample_jd_path = Path(__file__).parent / "sample_resumes" / "sample_job_description.txt"
                if sample_jd_path.exists():
                    st.session_state.target_jd_input = sample_jd_path.read_text(encoding="utf-8")
                    st.rerun()

        default_jd = st.session_state.get("target_jd_input", "")
        job_desc = st.text_area(
            "Job Description",
            value=default_jd,
            height=180,
            placeholder="Paste the full job description or target role requirements here...",
            label_visibility="collapsed",
        )

        col_run1, col_run2 = st.columns([3, 1])
        with col_run1:
            btn_run_ats = st.button("🔍 Analyse ATS Compatibility", use_container_width=True)
        with col_run2:
            btn_demo_ats = st.button("⚡ Quick Demo ATS", use_container_width=True, help="Load pre-computed ATS results for the sample resume")

        if btn_demo_ats:
            st.session_state.ats_result = DEMO_ATS_RESULT
            st.rerun()

        if btn_run_ats:
            if not job_desc.strip():
                st.warning("Please enter a job description or target role.")
            elif not _api_key_configured():
                st.session_state.ats_result = DEMO_ATS_RESULT
                st.info("💡 Displaying demo ATS analysis (configure Gemini API key for live custom analysis).")
                st.rerun()
            else:
                with st.spinner("🧠 Gemini is analysing ATS compatibility..."):
                    _sync_api_key()
                    result = analyse_ats_score(st.session_state.resume_text, job_desc)

                if result and not result.get("parse_error"):
                    st.session_state.ats_result = result
                    st.rerun()
                else:
                    st.error("Error analysing ATS compatibility with Gemini. Please try again.")

        # ── Display Results ───────────────────────────────────────────
        result = st.session_state.ats_result
        if result and not result.get("parse_error"):
            st.markdown("<br>", unsafe_allow_html=True)

            overall = result.get("overall_score", 0)

            # Top row: gauge + label
            g1, g2 = st.columns([1, 1])
            with g1:
                st.plotly_chart(_build_gauge(overall, "ATS Score"), use_container_width=True)
            with g2:
                st.markdown("<br><br>", unsafe_allow_html=True)
                label = _score_label(overall)
                st.markdown(
                    f"""
                    <div class="glass-card fade-in" style="text-align:center;">
                        <h2 style="color:{_score_color(overall)}; font-size:2.4rem; margin-bottom:4px;">
                            {label}
                        </h2>
                        <p style="color:#9CA3AF;">Your resume scored <strong style="color:#E8E8ED;">{overall}/100</strong>
                        on ATS compatibility.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("<br>", unsafe_allow_html=True)

            # Category scores breakdown
            cat_scores = result.get("category_scores", {})
            if cat_scores:
                st.markdown("### 📊 Category Breakdown")
                cats = list(cat_scores.keys())
                scores = [cat_scores[c].get("score", 0) for c in cats]

                # Radar chart
                st.plotly_chart(_build_radar(cats, scores), use_container_width=True)

                # Individual category cards
                cat_cols = st.columns(len(cats))
                for col, cat_name in zip(cat_cols, cats):
                    sc = cat_scores[cat_name].get("score", 0)
                    fb = cat_scores[cat_name].get("feedback", "")
                    with col:
                        st.markdown(
                            f"""
                            <div class="glass-card fade-in" style="text-align:center; min-height:160px;">
                                <div style="font-size:0.85rem; color:#9CA3AF; margin-bottom:4px;">{cat_name}</div>
                                <div style="font-size:1.8rem; font-weight:700; color:{_score_color(sc)};">
                                    {sc}%
                                </div>
                                <p style="font-size:0.8rem; color:#9CA3AF; margin-top:8px;">{fb}</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

            st.markdown("<br>", unsafe_allow_html=True)

            # Keywords row
            kw1, kw2 = st.columns(2)
            with kw1:
                st.markdown("#### ✅ Matched Keywords")
                matched_kw = result.get("matched_keywords", [])
                if matched_kw:
                    kw_html = " ".join(f'<span class="tag-matched">{k}</span>' for k in matched_kw)
                    st.markdown(kw_html, unsafe_allow_html=True)
                else:
                    st.info("No matched keywords identified.")

            with kw2:
                st.markdown("#### ❌ Missing Keywords")
                missing_kw = result.get("missing_keywords", [])
                if missing_kw:
                    kw_html = " ".join(f'<span class="tag-missing">{k}</span>' for k in missing_kw)
                    st.markdown(kw_html, unsafe_allow_html=True)
                else:
                    st.info("No critical missing keywords.")

            st.markdown("<br>", unsafe_allow_html=True)

            # Improvement suggestions
            suggestions = result.get("improvement_suggestions", [])
            if suggestions:
                st.markdown("### 💡 Actionable Improvement Tips")
                for tip in suggestions:
                    st.markdown(
                        f"""
                        <div class="tip-card fade-in">
                            <span style="color:#00D4AA; font-weight:600;">⚡ Tip:</span> {tip}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            # Executive summary
            if result.get("summary"):
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(
                    f"""
                    <div class="glass-card fade-in">
                        <h4 style="color:#8B83FF; margin-bottom:8px;">📋 Executive Summary</h4>
                        <p style="color:#E8E8ED; line-height:1.6; margin:0;">{result['summary']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    _render_footer()


# ═══════════════════════════════════════════════════════════════════════════════
# Page: Skill Gap Analysis
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "🔍  Skill Gap Analysis":
    st.markdown(
        '<h2 class="gradient-text">🔍 Skill Gap Analysis</h2>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="color:#9CA3AF;">Discover which skills you have and which ones you need for your target role.</p>',
        unsafe_allow_html=True,
    )

    if not _api_key_configured():
        _show_api_warning()

    if not st.session_state.resume_text:
        st.warning("⚠️ Please upload your resume first from the **📄 Upload Resume** page, or click **✨ 1-Click Demo Session** in the sidebar.")
    else:
        col_sg1, col_sg2 = st.columns([3, 1])
        with col_sg1:
            default_role = st.session_state.get("target_role_input", "")
            job_role = st.text_input(
                "Enter your Target Job Role",
                value=default_role,
                placeholder="e.g., Senior Full Stack / AI Engineer, Machine Learning Engineer",
            )
        with col_sg2:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            if st.button("📋 Sample Role"):
                st.session_state.target_role_input = "Senior Full Stack / AI Engineer"
                st.rerun()

        col_sgrun1, col_sgrun2 = st.columns([3, 1])
        with col_sgrun1:
            btn_run_sg = st.button("🔍 Analyse Skill Gap", use_container_width=True)
        with col_sgrun2:
            btn_demo_sg = st.button("⚡ Quick Demo Skill Gap", use_container_width=True)

        if btn_demo_sg:
            st.session_state.skill_gap_result = DEMO_SKILL_GAP_RESULT
            st.rerun()

        if btn_run_sg:
            if not job_role.strip():
                st.warning("Please enter a target job role.")
            elif not _api_key_configured():
                st.session_state.skill_gap_result = DEMO_SKILL_GAP_RESULT
                st.info("💡 Displaying demo Skill Gap analysis (configure Gemini API key for live custom analysis).")
                st.rerun()
            else:
                with st.spinner("🧠 Gemini is analysing your skill gap..."):
                    _sync_api_key()
                    result = analyse_skill_gap(st.session_state.resume_text, job_role)

                if result and not result.get("parse_error"):
                    st.session_state.skill_gap_result = result
                    st.rerun()
                else:
                    st.error("Error analysing skill gap with Gemini. Please try again.")

        # ── Display Results ───────────────────────────────────────────
        result = st.session_state.skill_gap_result
        if result and not result.get("parse_error"):
            st.markdown("<br>", unsafe_allow_html=True)

            match_pct = result.get("skill_match_percentage", 0)
            matched = result.get("matched_skills", [])
            missing = result.get("missing_skills", [])

            # Top overview row
            m1, m2, m3 = st.columns(3)
            m1.metric("Skill Match", f"{match_pct}%")
            m2.metric("Matched Skills", len(matched))
            m3.metric("Missing Skills", len(missing))

            st.markdown("<br>", unsafe_allow_html=True)

            # Gauge + visual bars
            v1, v2 = st.columns([1, 1])
            with v1:
                st.plotly_chart(_build_gauge(match_pct, "Skill Match"), use_container_width=True)
            with v2:
                st.markdown("#### Skills Overview")
                st.plotly_chart(_build_skill_bars(matched, missing), use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Matched skills detail
            if matched:
                st.markdown("#### ✅ Matched Skills")
                for item in matched:
                    with st.expander(f"**{item.get('skill', '')}** — {item.get('proficiency', '')}", expanded=True):
                        st.markdown(f"📝 *Evidence:* {item.get('evidence', 'N/A')}")

            # Missing skills detail
            if missing:
                st.markdown("#### ❌ Missing Skills — What to Learn")
                for item in missing:
                    importance = item.get("importance", "")
                    color_map = {"Critical": "#EF4444", "Important": "#F59E0B", "Nice-to-have": "#3B82F6"}
                    badge_color = color_map.get(importance, "#9CA3AF")
                    st.markdown(
                        f"""
                        <div class="skill-gap-card fade-in">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <strong style="color:#E8E8ED;">{item.get('skill', '')}</strong>
                                <span style="color:{badge_color}; font-size:0.82rem; font-weight:600;
                                    background:rgba(255,255,255,0.05); padding:2px 10px;
                                    border-radius:12px;">{importance}</span>
                            </div>
                            <p style="color:#9CA3AF; margin-top:8px; font-size:0.9rem; margin-bottom:0;">
                                💡 {item.get('recommendation', '')}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            if result.get("career_advice"):
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(
                    f"""
                    <div class="glass-card fade-in" style="margin-top:12px;">
                        <h4 style="color:#00D4AA; margin-bottom:8px;">🚀 Career Advice</h4>
                        <p style="color:#E8E8ED; line-height:1.7; margin:0;">{result['career_advice']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    _render_footer()


# ═══════════════════════════════════════════════════════════════════════════════
# Page: Mock Interview
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "🎤  Mock Interview":
    st.markdown(
        '<h2 class="gradient-text">🎤 AI Mock Interview</h2>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="color:#9CA3AF;">Practice with personalised interview questions and get instant AI feedback on your answers.</p>',
        unsafe_allow_html=True,
    )

    if not _api_key_configured():
        _show_api_warning()

    if not st.session_state.resume_text:
        st.warning("⚠️ Please upload your resume first from the **📄 Upload Resume** page, or click **✨ 1-Click Demo Session** in the sidebar.")
    else:
        # Configuration row
        col_int1, col_int2 = st.columns([3, 1])
        with col_int1:
            default_int_role = st.session_state.get("target_interview_role", "")
            job_role = st.text_input(
                "Target Role",
                value=default_int_role,
                placeholder="e.g., Senior Full Stack / AI Engineer",
                key="input_interview_role",
            )
        with col_int2:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            if st.button("📋 Sample Role", key="btn_sample_int_role"):
                st.session_state.target_interview_role = "Senior Full Stack / AI Engineer"
                st.rerun()

        c_diff, c_num = st.columns(2)
        with c_diff:
            difficulty = st.selectbox(
                "Difficulty",
                config.INTERVIEW_DIFFICULTY_LEVELS,
                index=1,
            )
        with c_num:
            num_q = st.selectbox(
                "Number of Questions",
                [3, 5, 7, 10],
                index=1,
            )

        col_qgen1, col_qgen2 = st.columns([3, 1])
        with col_qgen1:
            btn_qgen = st.button("🎯 Generate Interview Questions", use_container_width=True)
        with col_qgen2:
            btn_qdemo = st.button("⚡ Quick Demo Questions", use_container_width=True)

        if btn_qdemo:
            st.session_state.interview_questions = DEMO_INTERVIEW_QUESTIONS["questions"]
            st.session_state.current_question_idx = 0
            st.session_state.interview_scores = []
            st.session_state.evaluation_results = {}
            st.rerun()

        if btn_qgen:
            if not job_role.strip():
                st.warning("Please enter a target role.")
            elif not _api_key_configured():
                st.session_state.interview_questions = DEMO_INTERVIEW_QUESTIONS["questions"]
                st.session_state.current_question_idx = 0
                st.session_state.interview_scores = []
                st.session_state.evaluation_results = {}
                st.info("💡 Displaying demo interview questions (configure Gemini API key for live generation).")
                st.rerun()
            else:
                with st.spinner("🧠 Gemini is preparing your interview..."):
                    _sync_api_key()
                    result = generate_interview_questions(
                        st.session_state.resume_text,
                        job_role,
                        num_questions=num_q,
                        difficulty=difficulty,
                    )

                if result and not result.get("parse_error"):
                    st.session_state.interview_questions = result.get("questions", [])
                    st.session_state.current_question_idx = 0
                    st.session_state.interview_scores = []
                    st.session_state.evaluation_results = {}
                    st.rerun()
                else:
                    st.error("Error generating interview questions with Gemini. Please try again.")

        # ── Display Questions & Practice ──────────────────────────────
        questions = st.session_state.interview_questions
        if questions:
            st.markdown("<br>", unsafe_allow_html=True)

            # Progress bar
            total = len(questions)
            answered = len(st.session_state.evaluation_results)
            st.progress(answered / total, text=f"Progress: {answered}/{total} questions answered")

            st.markdown("<br>", unsafe_allow_html=True)

            # Question navigation tabs
            q_tabs = st.tabs([f"Q{i+1}" for i in range(total)])

            for idx, tab in enumerate(q_tabs):
                with tab:
                    q = questions[idx]
                    q_type = q.get("type", "General")
                    q_diff = q.get("difficulty", "Medium")
                    q_skill = q.get("related_skill", "")

                    # Question type & difficulty badges
                    type_class = f"badge-{q_type.lower()}" if q_type.lower() in ("technical", "behavioral", "situational") else "badge-skill"
                    diff_class = f"badge-{q_diff.lower()}" if q_diff.lower() in ("easy", "medium", "hard") else "badge-medium"

                    st.markdown(
                        f"""
                        <div style="display:flex; gap:8px; margin-bottom:12px; flex-wrap:wrap;">
                            <span class="badge {type_class}">{q_type}</span>
                            <span class="badge {diff_class}">{q_diff}</span>
                            <span class="badge badge-skill">🎯 {q_skill}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.markdown(
                        f"""
                        <div class="glass-card">
                            <h4 style="color:#E8E8ED; line-height:1.6; margin:0;">
                                Q{idx + 1}. {q.get('question', '')}
                            </h4>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.markdown("<br>", unsafe_allow_html=True)

                    # Quick sample answer loader for Q1
                    col_ans_lbl, col_ans_sample = st.columns([3, 1])
                    with col_ans_lbl:
                        st.markdown("##### Your Answer")
                    with col_ans_sample:
                        if idx == 0 and st.button("💡 Insert Sample Answer", key="btn_sample_ans_q0"):
                            st.session_state[f"ans_text_{idx}"] = (
                                "To achieve low latency and minimize hallucinations for 50k+ daily queries, "
                                "we implemented a multi-stage RAG pipeline. First, we utilized semantic chunking "
                                "with overlapping windows and indexed embeddings in Pinecone using HNSW indexing. "
                                "For queries, we combined dense vector similarity with BM25 lexical search using "
                                "Reciprocal Rank Fusion (RRF), followed by a cross-encoder re-ranker. We placed Redis "
                                "in front of the retrieval pipeline to cache frequent query embeddings and responses, "
                                "cutting p95 latency by 40%. Finally, strict prompt grounding guardrails instructed "
                                "the LLM to decline answering if context confidence fell below our calibrated threshold."
                            )
                            st.rerun()

                    default_ans = st.session_state.get(f"ans_text_{idx}", "")
                    answer = st.text_area(
                        "Your Answer",
                        value=default_ans,
                        height=150,
                        placeholder="Type your answer here...",
                        key=f"answer_{idx}",
                        label_visibility="collapsed",
                    )

                    col_sub1, col_sub2 = st.columns([3, 1])
                    with col_sub1:
                        btn_sub = st.button("📝 Submit & Get Feedback", key=f"submit_{idx}", use_container_width=True)
                    with col_sub2:
                        btn_sub_demo = st.button("⚡ Quick Feedback", key=f"demo_sub_{idx}", use_container_width=True)

                    if btn_sub_demo:
                        st.session_state.evaluation_results[idx] = DEMO_EVALUATION_RESULT
                        if DEMO_EVALUATION_RESULT.get("score") not in st.session_state.interview_scores:
                            st.session_state.interview_scores.append(DEMO_EVALUATION_RESULT.get("score"))
                        st.rerun()

                    if btn_sub:
                        if not answer.strip():
                            st.warning("Please type your answer before submitting.")
                        elif not _api_key_configured():
                            st.session_state.evaluation_results[idx] = DEMO_EVALUATION_RESULT
                            st.info("💡 Displaying demo evaluation (configure Gemini API key for live custom grading).")
                            st.rerun()
                        else:
                            with st.spinner("🧠 Gemini is evaluating your answer..."):
                                _sync_api_key()
                                evaluation = evaluate_answer(
                                    question=q.get("question", ""),
                                    what_to_look_for=q.get("what_to_look_for", ""),
                                    answer=answer,
                                )

                            if evaluation and not evaluation.get("parse_error"):
                                st.session_state.evaluation_results[idx] = evaluation
                                score = evaluation.get("score", 0)
                                if score not in [s for s in st.session_state.interview_scores]:
                                    st.session_state.interview_scores.append(score)
                                st.rerun()
                            else:
                                st.error("Error evaluating answer with Gemini.")

                    # ── Show evaluation if available ───────────────────
                    if idx in st.session_state.evaluation_results:
                        ev = st.session_state.evaluation_results[idx]
                        score = ev.get("score", 0)
                        label = ev.get("score_label", "")

                        score_color = "#10B981" if score >= 7 else "#F59E0B" if score >= 5 else "#EF4444"

                        st.markdown(
                            f"""
                            <div class="eval-card fade-in" style="border-left:4px solid {score_color}; margin-top:16px;">
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <h3 style="color:{score_color}; margin:0;">Score: {score}/10</h3>
                                    <span style="color:{score_color}; font-weight:600;">{label}</span>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        st.markdown("<br>", unsafe_allow_html=True)

                        fb1, fb2 = st.columns(2)
                        with fb1:
                            st.markdown("##### ✅ Strengths")
                            for s in ev.get("strengths", []):
                                st.markdown(f"- {s}")
                        with fb2:
                            st.markdown("##### 🔧 Areas for Improvement")
                            for imp in ev.get("improvements", []):
                                st.markdown(f"- {imp}")

                        st.markdown("<br>", unsafe_allow_html=True)

                        st.markdown("##### 💬 Detailed Feedback")
                        st.info(ev.get("detailed_feedback", ""))

                        with st.expander("📖 View Model Answer"):
                            st.markdown(ev.get("model_answer", ""))

                        if ev.get("tips"):
                            with st.expander("💡 Tips for Better Answers"):
                                for tip in ev["tips"]:
                                    st.markdown(f"- {tip}")

            # ── Session summary (when at least 2 answers) ─────────────
            if len(st.session_state.evaluation_results) >= 2:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("---")
                st.markdown("### 📈 Interview Session Summary")

                all_scores = [
                    st.session_state.evaluation_results[i].get("score", 0)
                    for i in sorted(st.session_state.evaluation_results)
                ]
                avg_score = sum(all_scores) / len(all_scores) if all_scores else 0

                s1, s2, s3 = st.columns(3)
                s1.metric("Avg. Score", f"{avg_score:.1f}/10")
                s2.metric("Questions Answered", len(all_scores))
                s3.metric("Best Score", f"{max(all_scores)}/10" if all_scores else "N/A")

                # Score trend line
                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x=[f"Q{i+1}" for i in sorted(st.session_state.evaluation_results)],
                        y=all_scores,
                        mode="lines+markers",
                        line={"color": "#6C63FF", "width": 3},
                        marker={"size": 10, "color": "#00D4AA", "line": {"width": 2, "color": "#6C63FF"}},
                        fill="tozeroy",
                        fillcolor="rgba(108,99,255,0.1)",
                    )
                )
                fig.update_layout(
                    height=300,
                    margin=dict(l=40, r=20, t=20, b=40),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis={"gridcolor": "#2D3148", "title": "Question", "color": "#9CA3AF"},
                    yaxis={
                        "gridcolor": "#2D3148",
                        "title": "Score",
                        "range": [0, 10.5],
                        "color": "#9CA3AF",
                    },
                    font={"color": "#E8E8ED", "family": "Inter"},
                )
                st.plotly_chart(fig, use_container_width=True)

    _render_footer()
