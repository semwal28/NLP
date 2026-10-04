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


def _initialise_model(model_name: Optional[str] = None, json_mode: bool = True) -> genai.GenerativeModel:
    """Configure the SDK and return a ``GenerativeModel`` instance."""
    genai.configure(api_key=config.GEMINI_API_KEY)
    kwargs: dict[str, Any] = {
        "max_output_tokens": config.MAX_OUTPUT_TOKENS,
        "temperature": config.TEMPERATURE,
        "top_p": config.TOP_P,
    }
    if json_mode:
        kwargs["response_mime_type"] = "application/json"

    generation_config = genai.types.GenerationConfig(**kwargs)
    return genai.GenerativeModel(
        model_name=model_name or config.GEMINI_MODEL,
        generation_config=generation_config,
    )


def _repair_json_string(s: str) -> str:
    """Apply heuristic repairs to common LLM JSON syntax errors."""
    # Fix trailing commas before closing braces/brackets
    s = re.sub(r",\s*([\]}])", r"\1", s)
    # Fix accidental punctuation like "id": 3> or "id": 3;
    s = re.sub(r'(:\s*\d+)[>;]', r'\1,', s)
    s = re.sub(r'(:\s*true)[>;]', r'\1,', s, flags=re.IGNORECASE)
    s = re.sub(r'(:\s*false)[>;]', r'\1,', s, flags=re.IGNORECASE)
    s = re.sub(r'(:\s*null)[>;]', r'\1,', s, flags=re.IGNORECASE)
    return s


def _clean_and_parse_json(text: str) -> Any:
    """Robustly extract and parse JSON from model responses.

    Handles markdown fences, leading/trailing conversational text, and common
    LLM output quirks.
    """
    raw = text.strip()

    # 1. Direct JSON parse attempt
    try:
        return json.loads(raw)
    except Exception:
        pass

    try:
        return json.loads(_repair_json_string(raw))
    except Exception:
        pass

    # 2. Extract content within ```json ... ``` or ``` ... ```
    fence_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    matches = re.findall(fence_pattern, raw)
    for block in matches:
        block = block.strip()
        try:
            return json.loads(block)
        except Exception:
            try:
                return json.loads(_repair_json_string(block))
            except Exception:
                pass

    # 3. Find outermost JSON object {...} or array [...]
    start_curly = raw.find("{")
    end_curly = raw.rfind("}")
    if start_curly != -1 and end_curly > start_curly:
        snippet = raw[start_curly : end_curly + 1].strip()
        try:
            return json.loads(snippet)
        except Exception:
            try:
                return json.loads(_repair_json_string(snippet))
            except Exception:
                pass

    start_bracket = raw.find("[")
    end_bracket = raw.rfind("]")
    if start_bracket != -1 and end_bracket > start_bracket:
        snippet = raw[start_bracket : end_bracket + 1].strip()
        try:
            return json.loads(snippet)
        except Exception:
            try:
                return json.loads(_repair_json_string(snippet))
            except Exception:
                pass

    raise json.JSONDecodeError("Could not extract valid JSON from model response", raw, 0)


def call_gemini(prompt: str) -> Optional[dict[str, Any]]:
    """Send a prompt to Gemini with automatic model fallback and JSON parsing.

    Args:
        prompt: The fully formatted prompt string.

    Returns:
        A parsed Python dictionary if the model returns valid JSON,
        or a dict with parse_error/error if it fails.

    Raises:
        ValueError: If the API key is not configured.
    """
    if not config.GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is not set. "
            "Please add it to your .env file."
        )

    # Build model sequence: configured model first, then fallback models
    models_to_try = [config.GEMINI_MODEL]
    for fb in getattr(config, "FALLBACK_MODELS", []):
        if fb not in models_to_try:
            models_to_try.append(fb)

    last_error: Optional[Exception] = None
    raw_text: str = ""

    for model_name in models_to_try:
        try:
            # First try with native JSON response mime type
            try:
                model = _initialise_model(model_name, json_mode=True)
                response = model.generate_content(prompt)
                raw_text = response.text or ""
            except Exception:
                # Fallback to standard mode if response_mime_type isn't supported by this model
                model = _initialise_model(model_name, json_mode=False)
                response = model.generate_content(prompt)
                raw_text = response.text or ""

            parsed = _clean_and_parse_json(raw_text)
            if isinstance(parsed, list):
                return {"data": parsed, "items": parsed}
            return parsed
        except Exception as exc:
            last_error = exc
            # Continue to next fallback model for any network, quota, or parsing error
            continue

    return {
        "raw_response": raw_text,
        "parse_error": True,
        "error": str(last_error) if last_error else "Model generation failed",
    }


def call_gemini_raw(prompt: str) -> str:
    """Send a prompt and return the raw text response (no JSON parsing).

    Useful when a non-JSON response is acceptable or expected.
    """
    if not config.GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is not set. "
            "Please add it to your .env file."
        )

    models_to_try = [config.GEMINI_MODEL]
    for fb in getattr(config, "FALLBACK_MODELS", []):
        if fb not in models_to_try:
            models_to_try.append(fb)

    last_error: Optional[Exception] = None
    for model_name in models_to_try:
        try:
            model = _initialise_model(model_name)
            response = model.generate_content(prompt)
            return response.text or ""
        except Exception as exc:
            last_error = exc
            err_str = str(exc).lower()
            if "not found" in err_str or "quota" in err_str or "429" in err_str or "404" in err_str:
                continue
            break

    return f"Error: {last_error}"
