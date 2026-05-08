import streamlit as st
import logging
import time
from pathlib import Path

# --- Project Structure Setup ---
import sys
sys.path.append(str(Path(__file__).parent))

# --- Local Imports ---
import utils
import llm_interface as llm  # Now uses Groq for inference

# --- Configuration & Logging ---
CONFIG = utils.load_config()
logger = utils.setup_logging(CONFIG)

# --- Constants from Config ---
APP_CONFIG = CONFIG.get('app', {})
LLM_CONFIG = CONFIG.get('llm', {})
PROMPTS_CONFIG = CONFIG.get('prompts', {})

PAGE_TITLE = APP_CONFIG.get('title', " Symptra")
PAGE_ICON = APP_CONFIG.get('page_icon', "🩺")
MENU_ITEMS = APP_CONFIG.get('menu_items', {})

DEFAULT_MODEL = LLM_CONFIG.get('default_model', "llama-3.1-8b-instant")
FALLBACK_MODEL = LLM_CONFIG.get('fallback_model', "llama-3.3-70b-versatile")
# Extract LLM parameters directly, filter out model names
LLM_PARAMS = {k: v for k, v in LLM_CONFIG.items() if k not in ['default_model', 'fallback_model']}

SYSTEM_PROMPT = PROMPTS_CONFIG.get('system_prompt', "You are Symptra, a helpful AI assistant.")
INITIAL_MSG = PROMPTS_CONFIG.get('initial_assistant_message', "How can I help?")
ERROR_MSG = PROMPTS_CONFIG.get('error_message', "Sorry, an error occurred.")
DISCLAIMER_SHORT = PROMPTS_CONFIG.get('disclaimer_short', "Not medical advice.")
DISCLAIMER_LONG = PROMPTS_CONFIG.get('disclaimer_long', "This is not medical advice. Consult a doctor.")

# --- Streamlit Page Setup ---
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    menu_items=MENU_ITEMS
)

# --- Initialize LLM Clients (Groq) ---
# Cache clients to avoid re-initialization on every interaction
@st.cache_resource
def get_clients():
    api_client = llm.get_hf_api_client()
    inference_client = llm.get_hf_inference_client()
    return api_client, inference_client

hf_api_client, hf_inference_client = get_clients()
hf_available = hf_inference_client is not None

# --- State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": INITIAL_MSG}
    ]
if "selected_model" not in st.session_state:
    st.session_state.selected_model = DEFAULT_MODEL
if "request_count" not in st.session_state:
    st.session_state.request_count = 0

MAX_REQUESTS_PER_SESSION = 15  # Cap per visitor session to protect free-tier quota

if "hf_available" not in st.session_state:
    st.session_state.hf_available = hf_available
    if not hf_available:
        logger.error("Groq client initialization failed. Check API key in secrets.")


# --- Sidebar ---
with st.sidebar:
    st.title("Settings & Info")
    st.divider()

    # Model Selection
    st.subheader("LLM Configuration")

    if not st.session_state.hf_available:
        st.error("🔴 Groq client failed to initialize. Check API key in Streamlit secrets (`groq.api_key`).")
        model_options = [st.session_state.selected_model]
        st.info(f"Configured model: `{st.session_state.selected_model}`. API connection failed.")
    else:
        # Fetch models only if client is available
        @st.cache_data(ttl=3600)  # Cache for 1 hour
        def cached_get_models(_client):
            return llm.get_available_hf_models(hf_api_client)

        available_models = cached_get_models(hf_api_client)

        if not available_models:
            st.warning("Could not fetch models. Using configured default.")
            model_options = [st.session_state.selected_model]
            if FALLBACK_MODEL and st.session_state.selected_model != FALLBACK_MODEL:
                model_options.append(FALLBACK_MODEL)
        else:
            model_options = available_models
            # Ensure default and selected models are in the list for the dropdown
            if st.session_state.selected_model not in model_options:
                model_options.insert(0, st.session_state.selected_model)
            if DEFAULT_MODEL not in model_options:
                model_options.insert(0, DEFAULT_MODEL)

        # Find index of currently selected model
        try:
            current_index = model_options.index(st.session_state.selected_model)
        except ValueError:
            st.warning(f"Selected model {st.session_state.selected_model} not in available list. Defaulting selection.")
            current_index = 0
            st.session_state.selected_model = model_options[0]

        selected = st.selectbox(
            "Select LLM Model (Groq):",
            options=list(set(model_options)),  # Ensure unique options
            index=current_index,
            help="Choose an instruction-following model hosted on Groq."
        )
        if selected != st.session_state.selected_model:
            logger.info(f"User selected model: {selected}")
            st.session_state.selected_model = selected
            st.success(f"Switched to model: `{selected}`")

    st.caption(f"Using: `{st.session_state.selected_model}`")

    # Session message counter
    st.caption(f"Messages this session: {st.session_state.request_count} / {MAX_REQUESTS_PER_SESSION}")

    # Clear Chat Button
    st.divider()
    if st.button("Clear Chat History", key="clear_chat"):
        logger.info("Chat history cleared by user.")
        st.session_state.messages = [
            {"role": "assistant", "content": INITIAL_MSG}
        ]
        st.rerun()

    # Important Notes / Disclaimer
    st.divider()
    st.error(DISCLAIMER_SHORT)  # Short, always visible disclaimer
    with st.expander("⚠️ Show Full Disclaimer & Important Notes"):
        st.warning(DISCLAIMER_LONG)
        st.markdown("---")
        st.markdown(f"**Model:** `{st.session_state.selected_model}` (via Groq)")
        st.markdown("**Status:** " + ("🟢 Connected to Groq" if st.session_state.hf_available else "🔴 Groq Connection Failed"))
        st.markdown("**Developer:** Naga Sai")


# --- Main Chat Interface ---
st.title(PAGE_TITLE)
st.warning(DISCLAIMER_LONG, icon="⚠️")  # Prominent main disclaimer

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("Describe symptoms here... (e.g., 'headache and fatigue')"):
    # Per-session rate limit (protects free-tier Groq quota from abuse)
    if st.session_state.request_count >= MAX_REQUESTS_PER_SESSION:
        st.error(
            f"⏳ You've reached the demo limit of {MAX_REQUESTS_PER_SESSION} messages "
            "for this session. Please refresh the page to start a new session. "
            "This limit helps keep Symptra available for everyone."
        )
        st.stop()
    st.session_state.request_count += 1
    logger.info(f"User input received (request #{st.session_state.request_count}): {prompt[:50]}...")

    # Add user message to state and display
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate and display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        full_response = ""
        try:
            # Ensure Groq client is available
            if not st.session_state.hf_available or hf_inference_client is None:
                raise llm.LLMError("Groq Inference Client is unavailable. Cannot process request.")

            # Start streaming response from LLM
            response_stream = llm.get_hf_llm_response_stream(
                client=hf_inference_client,
                model_id=st.session_state.selected_model,
                messages=st.session_state.messages,  # Pass full history for formatting
                system_prompt=SYSTEM_PROMPT,  # Pass system prompt separately
                llm_params=LLM_PARAMS
            )

            # Stream response to the UI
            for chunk in response_stream:
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")  # Simulate typing cursor

            message_placeholder.markdown(full_response)  # Final response display

        except llm.LLMError as e:
            logger.error(f"LLMError encountered: {e}", exc_info=False)
            full_response = f"{ERROR_MSG}\n\n**Details:** {e}"
            message_placeholder.error(full_response)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}", exc_info=True)
            full_response = ERROR_MSG
            message_placeholder.error(full_response)

    # Add final assistant response (or error message) to state only if successful or known error
    if full_response:
        st.session_state.messages.append({"role": "assistant", "content": full_response})