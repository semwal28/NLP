"""
Demo Data Module for AI Resume Analyzer & Interview Prep Coach.

Provides realistic sample analysis data corresponding to Alex Morgan's
sample resume and the Senior Full Stack / AI Engineer role. Used for instant
demonstration, offline previewing, and automated UI testing.
"""

from typing import Any

DEMO_PARSED_RESUME: dict[str, Any] = {
    "name": "Alex Morgan",
    "email": "alex.morgan@email.com",
    "phone": "+1 (555) 234-5678",
    "linkedin": "linkedin.com/in/alexmorgan",
    "summary": "Results-driven Senior Full Stack & AI Engineer with 5+ years of experience designing scalable microservices, building intelligent NLP applications, and deploying machine learning models into production. Proven track record in reducing cloud costs by 30% and accelerating API response times by 45%.",
    "skills": [
        "Python", "TypeScript", "JavaScript", "SQL", "Bash",
        "FastAPI", "Flask", "React", "Node.js", "PyTorch", "LangChain", "Transformers", "Scikit-learn",
        "AWS (EC2, S3, Lambda)", "Docker", "Kubernetes", "CI/CD", "PostgreSQL", "Redis",
        "Prompt Engineering", "Embeddings", "RAG Architectures", "Vector Databases (Pinecone, ChromaDB)"
    ],
    "experience": [
        {
            "title": "Senior Software Engineer",
            "company": "TechNova Solutions, San Francisco, CA",
            "duration": "Jan 2022 - Present",
            "highlights": [
                "Architected and deployed an enterprise NLP document assistant handling 50k+ daily queries, reducing manual review time by 60%.",
                "Designed low-latency RESTful APIs using FastAPI and Redis caching, improving throughput by 40%.",
                "Led a team of 4 engineers in migrating monolithic legacy services to Dockerized microservices on AWS EKS.",
                "Implemented automated CI/CD pipelines reducing deployment failure rate from 12% to under 1%."
            ]
        },
        {
            "title": "Software Engineer",
            "company": "DataBridge Analytics, Austin, TX",
            "duration": "Aug 2019 - Dec 2021",
            "highlights": [
                "Developed predictive data pipelines processing 2TB+ daily telemetry data using Python and Apache Spark.",
                "Collaborated with product designers to build modern, responsive React dashboards with real-time analytics.",
                "Authored unit and integration test suites with 92% code coverage, cutting production bug incidents by 35%."
            ]
        }
    ],
    "education": [
        {
            "degree": "Bachelor of Science in Computer Science",
            "institution": "University of California, Berkeley",
            "year": "2015 - 2019"
        }
    ],
    "certifications": [
        "AWS Certified Solutions Architect – Associate",
        "DeepLearning.AI Natural Language Processing Specialization"
    ],
    "projects": [
        {
            "name": "AI Resume & Career Coach",
            "description": "Streamlit and LLM-powered application providing ATS scoring, skill gap detection, and real-time interview evaluation."
        },
        {
            "name": "Neural Search Engine",
            "description": "Vector-based semantic search platform utilizing sentence transformers and Milvus for fast document retrieval."
        }
    ]
}

DEMO_ATS_RESULT: dict[str, Any] = {
    "overall_score": 88,
    "category_scores": {
        "Keyword Relevance": {
            "score": 92,
            "feedback": "Outstanding alignment with core technical keywords: FastAPI, Python, React, LLMs, Docker, AWS, and RAG architectures."
        },
        "Format & Structure": {
            "score": 90,
            "feedback": "Standard reverse-chronological structure with clearly labeled sections, consistent bullet points, and high parseability."
        },
        "Section Completeness": {
            "score": 95,
            "feedback": "All fundamental sections are present: Summary, Technical Skills, Professional Experience, Education, and Key Projects."
        },
        "Impact & Metrics": {
            "score": 84,
            "feedback": "Excellent use of metrics (50k+ queries, 60% review reduction, 40% throughput increase). Could add more business ROI impact in the earlier role."
        },
        "Overall Readability": {
            "score": 90,
            "feedback": "Concise language, active verbs, and clear distinction between technologies and responsibilities."
        }
    },
    "matched_keywords": [
        "Python", "FastAPI", "React", "Docker", "AWS", "LLM", "NLP",
        "RAG", "PostgreSQL", "Redis", "TypeScript", "CI/CD", "Vector Databases"
    ],
    "missing_keywords": [
        "Prometheus", "Grafana", "Datadog", "Open-source fine-tuning", "LlamaIndex"
    ],
    "improvement_suggestions": [
        "Mention observability tools (e.g. Grafana or Datadog) used during your AWS deployments to cover monitoring requirements.",
        "Highlight any experience fine-tuning open-source LLMs (like Llama or Mistral) alongside proprietary API integrations.",
        "Add a brief mention of LlamaIndex or alternative RAG orchestrators to demonstrate breadth in modern GenAI frameworks."
    ],
    "summary": "Alex's profile is a top-tier fit for the Senior Full Stack / AI Engineer role, scoring an impressive 88/100 on ATS compatibility. With strong demonstrated achievements in FastAPI, LLM architectures, React, and cloud infrastructure, addressing minor observability keyword gaps will elevate this resume to the top 1% of applicants."
}

DEMO_SKILL_GAP_RESULT: dict[str, Any] = {
    "candidate_skills": [
        "Python", "TypeScript", "FastAPI", "React", "Docker", "AWS",
        "PyTorch", "LangChain", "RAG", "Vector Databases", "PostgreSQL", "Redis"
    ],
    "required_skills": [
        "Python", "TypeScript", "FastAPI", "React", "Docker", "AWS",
        "LLMs", "RAG", "Kubernetes", "Observability (Grafana/Datadog)", "Model Fine-Tuning"
    ],
    "matched_skills": [
        {
            "skill": "Python & FastAPI Microservices",
            "proficiency": "Strong",
            "evidence": "Designed low-latency RESTful APIs with Redis caching handling 50k+ daily queries at TechNova Solutions."
        },
        {
            "skill": "GenAI & RAG Architectures",
            "proficiency": "Strong",
            "evidence": "Built enterprise NLP document assistant with LangChain and vector databases (Pinecone/ChromaDB)."
        },
        {
            "skill": "Full Stack Development (React/TS)",
            "proficiency": "Strong",
            "evidence": "Collaborated on modern telemetry dashboards and responsive AI interfaces."
        },
        {
            "skill": "Cloud & Containerization (AWS / Docker)",
            "proficiency": "Strong",
            "evidence": "Migrated legacy monolith to Dockerized microservices on AWS EKS with automated CI/CD."
        }
    ],
    "missing_skills": [
        {
            "skill": "Cloud Observability & Telemetry (Grafana, Datadog)",
            "importance": "Important",
            "recommendation": "Set up Prometheus and Grafana dashboards for existing FastAPI microservices to gain hands-on production monitoring experience."
        },
        {
            "skill": "Open-Source LLM Fine-Tuning (PEFT, LoRA)",
            "importance": "Nice-to-have",
            "recommendation": "Complete a hands-on project using Hugging Face PEFT/LoRA to fine-tune Llama 3 or Mistral on a domain-specific dataset."
        }
    ],
    "skill_match_percentage": 85,
    "overall_assessment": "The candidate has an 85% skill alignment with the Senior Full Stack / AI Engineer profile. Core software engineering, full stack architecture, and GenAI capabilities are exceptional.",
    "career_advice": "Focus next on cloud observability (Datadog/Grafana) and parameter-efficient fine-tuning (PEFT/LoRA) to transition from an applied AI engineer to a full-lifecycle AI systems architect."
}

DEMO_INTERVIEW_QUESTIONS: dict[str, Any] = {
    "questions": [
        {
            "id": 1,
            "question": "In your resume, you mention architecting an enterprise NLP assistant that processes 50k+ daily queries. How did you design the retrieval pipeline to maintain low latency while avoiding hallucination?",
            "type": "Technical",
            "difficulty": "Medium",
            "what_to_look_for": "Discussion of chunking strategies, hybrid search (keyword + vector), re-ranking models, prompt guardrails, and Redis caching for recurring queries.",
            "related_skill": "RAG Architecture & Latency Optimization"
        },
        {
            "id": 2,
            "question": "Can you walk through your experience migrating a monolithic service to Dockerized microservices on AWS EKS? What was your rollback and zero-downtime deployment strategy?",
            "type": "Technical",
            "difficulty": "Hard",
            "what_to_look_for": "Use of canary or blue-green deployments, Helm charts, ingress controllers, database migration isolation, and health check probes.",
            "related_skill": "Kubernetes & Microservices Architecture"
        },
        {
            "id": 3,
            "question": "Describe a scenario where a production LLM feature began returning low-quality or hallucinated responses after a model version update. How did you diagnose and remediate the issue?",
            "type": "Situational",
            "difficulty": "Medium",
            "what_to_look_for": "Structured troubleshooting: logging evaluation datasets, prompt regression testing, temperature adjustment, grounding checks, and fallback mechanisms.",
            "related_skill": "LLM Quality Assurance & Debugging"
        },
        {
            "id": 4,
            "question": "As a senior engineer leading 4 teammates, tell me about a time when your team disagreed on an architectural choice (e.g. FastAPI vs. Node.js). How did you reach consensus?",
            "type": "Behavioral",
            "difficulty": "Medium",
            "what_to_look_for": "Objective evaluation criteria (POCs, benchmarks, team familiarity), active listening, blameless decision matrices, and driving team buy-in.",
            "related_skill": "Engineering Leadership & Collaboration"
        },
        {
            "id": 5,
            "question": "How do you handle security and data privacy when sending sensitive enterprise documents to commercial LLM APIs?",
            "type": "Technical",
            "difficulty": "Medium",
            "what_to_look_for": "PII redaction, zero-data-retention agreements, encryption in transit/rest, tenant-isolated vector namespaces, and audit logging.",
            "related_skill": "AI Security & Compliance"
        }
    ]
}

DEMO_EVALUATION_RESULT: dict[str, Any] = {
    "score": 9,
    "score_label": "Very Good",
    "strengths": [
        "Clearly articulated the end-to-end RAG architecture with concrete technical details.",
        "Highlighted the practical trade-offs between dense semantic retrieval and sparse BM25 keyword matching.",
        "Demonstrated production awareness by including Redis caching and re-ranking steps to optimize both latency and relevance."
    ],
    "improvements": [
        "Could briefly specify exact target latency SLA numbers (e.g., p95 < 250ms).",
        "Could mention automated evaluation metrics like Ragas or TruLens for measuring groundedness."
    ],
    "detailed_feedback": "Your answer demonstrates deep, hands-on production experience with modern retrieval-augmented generation architectures. You addressed both relevance and latency systematically, showing maturity beyond theoretical understanding.",
    "model_answer": "To achieve low latency and minimize hallucinations for 50k+ daily queries, we implemented a multi-stage RAG pipeline. First, we utilized semantic chunking with overlapping windows and indexed embeddings in Pinecone using HNSW indexing. For queries, we combined dense vector similarity with BM25 lexical search using Reciprocal Rank Fusion (RRF), followed by a lightweight cross-encoder re-ranker for the top 5 chunks. We placed Redis in front of the retrieval pipeline to cache frequent query embeddings and responses, cutting p95 latency by 40%. Finally, strict prompt grounding guardrails instructed the LLM to decline answering if the context confidence fell below our calibrated threshold.",
    "tips": [
        "Quantify your results with percentiles (p50, p95, p99) when discussing latency optimizations.",
        "Mention framework names for evaluation (e.g., Ragas, TruLens) to reinforce technical rigor."
    ]
}
