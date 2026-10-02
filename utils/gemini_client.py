"""
Gemini API Client Module.

A lightweight wrapper around the Google Generative AI SDK that handles
model initialisation, request construction, and error handling for every
API call the application makes.
"""

from __future__ import annotations

import json
import re
from typing import Any, Optional

import google.generativeai as genai

import config


def _initialise_model() -> genai.GenerativeModel:
    """Configure the SDK and return a ``GenerativeModel`` instance."""
    genai.configure(api_key=config.GEMINI_API_KEY)
    generation_config = genai.types.GenerationConfig(
        max_output_tokens=config.MAX_OUTPUT_TOKENS,
        temperature=config.TEMPERATURE,
        top_p=config.TOP_P,
    )
    return genai.GenerativeModel(
        model_name=config.GEMINI_MODEL,
        generation_config=generation_config,
    )


def _clean_json_response(text: str) -> str:
    """Strip markdown code fences and other noise from the model response.

    The model occasionally wraps its JSON output in ```json ... ``` blocks
    despite being instructed not to. This helper removes such wrappers.
    """
    # Remove markdown code fences (```json ... ``` or ``` ... ```)
    cleaned = re.sub(r"^```(?:json)?\s*\n?", "", text.strip())
    cleaned = re.sub(r"\n?```\s*$", "", cleaned)
    return cleaned.strip()


def call_gemini(prompt: str) -> Optional[dict[str, Any]]:
    """Send a prompt to Gemini and return the parsed JSON response.

    Args:
        prompt: The fully formatted prompt string.

    Returns:
        A parsed Python dictionary if the model returns valid JSON,
        or ``None`` if an error occurs.

    Raises:
        ValueError: If the API key is not configured.
    """
    if not config.GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is not set. "
            "Please add it to your .env file."
        )

    model = _initialise_model()
    try:
        response = model.generate_content(prompt)
        raw_text = response.text
        cleaned = _clean_json_response(raw_text)
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # If JSON parsing fails, return the raw text wrapped in a dict
        return {"raw_response": raw_text, "parse_error": True}
    except Exception as exc:
        return {"error": str(exc), "parse_error": True}


def call_gemini_raw(prompt: str) -> str:
    """Send a prompt and return the raw text response (no JSON parsing).

    Useful when a non-JSON response is acceptable or expected.
    """
    if not config.GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is not set. "
            "Please add it to your .env file."
        )

    model = _initialise_model()
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as exc:
        return f"Error: {exc}"
