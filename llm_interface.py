import streamlit as st
import logging
from typing import List, Dict, Iterator, Any
from groq import Groq
import requests

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Custom exception for LLM interaction errors."""
    pass


# --- Groq API Configuration ---
GROQ_API_KEY = st.secrets.get("groq", {}).get("api_key")


def get_hf_api_client():
    """Kept for compatibility with app.py."""
    return "groq"  # Truthy placeholder


def get_hf_inference_client() -> Groq | None:
    """Initializes and returns a Groq client if API key is available."""
    if not GROQ_API_KEY:
        logger.warning("Groq API key not found in Streamlit secrets.")
        st.error("Groq API key is missing from Streamlit Secrets (`[groq] api_key`).", icon="🚨")
        return None
    try:
        return Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize Groq client: {e}", exc_info=True)
        return None


def check_hf_model_availability(model_id: str, client: Groq | None) -> bool:
    """Checks if a model is reachable via Groq."""
    if not client:
        return False
    try:
        client.chat.completions.create(
            messages=[{"role": "user", "content": "hi"}],
            model=model_id,
            max_tokens=1,
        )
        return True
    except Exception as e:
        logger.warning(f"Model availability check failed for '{model_id}': {e}")
        return False

def get_available_hf_models(client, task_filter="text-generation") -> List[str]:
    """Returns a curated list of currently-active production Groq models."""
    return [
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "openai/gpt-oss-120b",
        "moonshotai/kimi-k2-instruct-0905",
        "qwen/qwen3-32b",
    ]


def format_messages_for_chat(
    messages: List[Dict[str, str]],
    system_prompt: str | None = None,
) -> List[Dict[str, str]]:
    """Formats messages for Groq's chat completions API."""
    formatted: List[Dict[str, str]] = []
    if system_prompt:
        formatted.append({"role": "system", "content": system_prompt})

    for msg in messages:
        role = msg.get("role")
        content = msg.get("content")
        if role in ("user", "assistant") and content:
            formatted.append({"role": role, "content": content})

    return formatted


def get_hf_llm_response_stream(
    client: Groq,
    model_id: str,
    messages: List[Dict[str, str]],
    system_prompt: str | None,
    llm_params: Dict[str, Any],
) -> Iterator[str]:
    """Gets a streamed response from Groq."""
    if not client:
        raise LLMError("Groq client is not initialized.")

    user_assistant_messages = [m for m in messages if m.get("role") != "system"]
    chat_messages = format_messages_for_chat(user_assistant_messages, system_prompt)

    logger.info(f"Requesting streaming chat completion from Groq model: {model_id}")

    chat_params: Dict[str, Any] = {}

    if "max_new_tokens" in llm_params:
        chat_params["max_tokens"] = llm_params["max_new_tokens"]
    elif "max_tokens" in llm_params:
        chat_params["max_tokens"] = llm_params["max_tokens"]
    else:
        chat_params["max_tokens"] = 512

    if "temperature" in llm_params:
        chat_params["temperature"] = llm_params["temperature"]
    if "top_p" in llm_params:
        chat_params["top_p"] = llm_params["top_p"]

    try:
        stream = client.chat.completions.create(
            messages=chat_messages,
            model=model_id,
            stream=True,
            **chat_params,
        )

        generated_text = ""
        for chunk in stream:
            try:
                content = chunk.choices[0].delta.content
            except (AttributeError, IndexError):
                content = None

            if content:
                generated_text += content
                yield content

        logger.info(f"Finished streaming from {model_id}. Length: {len(generated_text)}")
        if not generated_text.strip() and len(chat_messages) > 0:
            logger.warning(f"Model {model_id} returned an empty response.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error connecting to Groq API: {e}", exc_info=True)
        raise LLMError(f"Network error: Could not connect to Groq API. {e}") from e
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error during Groq API call: {error_message}", exc_info=True)

        if "rate_limit" in error_message.lower() or "rate limit" in error_message.lower():
            raise LLMError("Rate limit reached on Groq. Please wait a moment and try again.") from e
        elif "model_not_found" in error_message.lower() or "not found" in error_message.lower():
            raise LLMError(f"Model '{model_id}' not found on Groq. Try 'llama-3.3-70b-versatile' instead.") from e
        elif "invalid_api_key" in error_message.lower() or "authentication" in error_message.lower():
            raise LLMError("Invalid Groq API key. Check your secrets.toml file.") from e
        else:
            raise LLMError(f"Failed to get response from Groq API: {e}") from e