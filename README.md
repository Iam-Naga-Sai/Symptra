\# 🩺 Symptra



> \*\*Understand before you worry.\*\*



An AI-powered symptom information chatbot built with Streamlit and Groq's Llama models. Symptra provides general health information in a conversational format — always with safety guardrails redirecting users to qualified medical professionals.



> ⚠️ \*\*Disclaimer:\*\* Symptra is a demonstration project for informational purposes only. It is \*\*NOT a medical device\*\* and does \*\*NOT provide medical advice or diagnosis\*\*. Always consult a qualified healthcare provider for any health concerns.



🔗 \*\*Live Demo:\*\* \[Try Symptra](https://your-streamlit-url.streamlit.app)



\---



\## ✨ Features



\- 💬 \*\*Conversational interface\*\* — natural chat about health symptoms

\- 🛡️ \*\*Built-in safety guardrails\*\* — refuses diagnoses, escalates emergencies, mandates disclaimers

\- ⚡ \*\*Sub-second responses\*\* — powered by Groq's LPU inference

\- 🔄 \*\*Streaming output\*\* — real-time word-by-word response generation

\- 🎛️ \*\*Configurable models\*\* — swap between Llama 3.1 8B, Llama 3.3 70B, and others

\- 🧱 \*\*Production-ready architecture\*\* — clean separation of config, LLM interface, and UI layers

\- ⏱️ \*\*Per-session rate limiting\*\* — protects the demo's free-tier quota from abuse



\---



\## 🛠️ Tech Stack



| Layer | Technology |

|---|---|

| \*\*Frontend\*\* | Streamlit |

| \*\*LLM Provider\*\* | Groq (Llama 3.1 / 3.3) |

| \*\*Language\*\* | Python 3.10+ |

| \*\*Configuration\*\* | YAML |

| \*\*Deployment\*\* | Streamlit Community Cloud |



\---



\## 🚀 Local Development



\### Prerequisites



\- Python 3.10+

\- A free \[Groq API key](https://console.groq.com/keys)



\### Setup



```bash

\# Clone the repo

git clone https://github.com/nagasain2710-crypto/Symptra.git

cd Symptra



\# Create and activate virtual environment

python -m venv venv



\# Windows:

venv\\Scripts\\activate



\# macOS / Linux:

source venv/bin/activate



\# Install dependencies

pip install -r requirements.txt

```



\### Configure Secrets



Create a file at `.streamlit/secrets.toml`:



```toml

\[groq]

api\_key = "gsk\_YOUR\_GROQ\_API\_KEY"

```



⚠️ \*\*Never commit this file\*\* — it's already in `.gitignore`.



\### Run



```bash

streamlit run app.py

```



Open `http://localhost:8501` in your browser.



\---



\## 🧠 Safety Architecture



Symptra's system prompt enforces several non-negotiable constraints:



1\. \*\*Never diagnose\*\* — discusses \*types\* of conditions for doctor-discussion only

2\. \*\*Mandatory disclaimers\*\* — every response begins and ends with a medical disclaimer

3\. \*\*Emergency escalation\*\* — symptoms suggesting urgency trigger immediate "seek emergency care" responses

4\. \*\*No prescriptions\*\* — refuses medication or treatment recommendations

5\. \*\*No PII collection\*\* — never asks for personally identifiable information

6\. \*\*Per-session rate limiting\*\* — caps requests at 15/session to protect free-tier quota



\---



\## 🎯 Example Interactions



\*\*User:\*\* "I have a mild headache and feel a bit tired."



\*\*Symptra:\*\* \*Provides general information about possible causes (stress, sleep, hydration, etc.), recommends seeing a doctor, includes mandatory disclaimer.\*



\*\*User:\*\* "I have severe chest pain and difficulty breathing."



\*\*Symptra:\*\* \*Immediately recommends emergency medical attention before providing any other information.\*



\*\*User:\*\* "What medication should I take?"



\*\*Symptra:\*\* \*Politely refuses, reiterates need to consult a healthcare provider.\*



\---



\## ⚠️ Important Disclaimers



\- This is a \*\*demonstration project\*\*, not a medical device

\- AI can produce \*\*inaccurate, incomplete, or biased information\*\*

\- \*\*Never use this tool for self-diagnosis\*\* or to make health decisions

\- \*\*Always consult a qualified healthcare provider\*\* for medical concerns

\- \*\*In emergencies, call your local emergency services immediately\*\*



\---



\## 📜 License



MIT License — feel free to use this as a learning resource.



\---



\## 👤 Author



\*\*Naga Sai\*\*



\[GitHub](https://github.com/nagasain2710-crypto)



\---



\*Built as a demonstration of safe, responsible AI deployment in sensitive domains.\*

