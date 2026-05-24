# AutoStream — Conversational AI Sales Agent

A **stateful conversational AI agent** for a fictional SaaS company called AutoStream, which sells automated video editing tools for content creators. The agent identifies user intent, answers product questions from a local knowledge base, qualifies sales leads across multiple turns, and captures lead data once all required fields are collected.

Built with **Python**, **LangGraph**, and **Streamlit** — runs as both an interactive CLI and a web chat UI.

---

## What It Does

The agent handles three types of conversations:

| Intent | Example message | Agent behaviour |
|---|---|---|
| Casual greeting | *"Hi, hello"* | Friendly welcome, offers help |
| Product / pricing inquiry | *"What are your plans? How much does Pro cost?"* | Retrieves answer from local JSON knowledge base |
| High-intent lead | *"I want to sign up for Pro"* | Starts lead qualification — collects name, email, platform, then fires `mock_lead_capture()` |

State persists across turns — the agent remembers partial lead data and picks up exactly where it left off.

---

## Architecture

The agent is modelled as a **LangGraph state machine** with five nodes:

```
User message
     │
     ▼
┌─────────┐
│  intent │  ← classifies message: greeting / inquiry / high_intent_lead
└────┬────┘
     │
     ├── greeting / inquiry ──────────────────► retrieval ──► respond ──► END
     │
     └── high_intent_lead / partial lead ──► lead_router
                                                   │
                                          ┌────────┴────────┐
                                          │                 │
                                     need more info    all fields collected
                                          │                 │
                                       respond           tool (mock_lead_capture)
                                          │                 │
                                         END              END
```

### Node responsibilities

| Node | File | What it does |
|---|---|---|
| `intent` | `agent/intent.py` | Keyword-based intent classifier + entity extractor (name, email, platform) |
| `retrieval` | `agent/rag.py` | Fetches relevant text from `data/knowledge.json` |
| `lead_router` | `agent/graph.py` | Checks which lead fields are missing; sets `next_action` |
| `respond` | `agent/graph.py` | Generates contextual response based on intent and state |
| `tool` | `agent/tools.py` | Calls `mock_lead_capture(name, email, platform)` once all fields are present |

### State

All nodes share a `ChatState` TypedDict (defined in `agent/state.py`) that carries messages, intent, retrieved context, lead fields, and completion flags across turns.

---

## Project Structure

```
Autostream-ai-agent/
├── agent/
│   ├── graph.py        # LangGraph workflow: nodes, edges, conditional routing
│   ├── intent.py       # Intent classification and entity extraction
│   ├── rag.py          # Local knowledge base retrieval
│   ├── state.py        # ChatState TypedDict definition
│   └── tools.py        # mock_lead_capture tool
├── data/
│   └── knowledge.json  # AutoStream product info, pricing, FAQs, policies
├── app.py              # Streamlit web chat UI
├── main.py             # CLI interface (terminal chat loop)
├── demo_script.txt     # Suggested demo conversation walkthrough
├── requirements.txt    # Python dependencies
├── .gitignore
├── LICENSE
└── README.md
```

---

## Getting Started

### Prerequisites
- Python 3.9+

### Installation

```bash
# Clone the repository
git clone https://github.com/thanujaa-5520/Autostream-ai-agent.git
cd Autostream-ai-agent

# Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Running the Agent

### Option 1 — Streamlit web UI (recommended for demos)

```bash
streamlit run app.py
```

Opens at [http://localhost:8501](http://localhost:8501). Chat in the browser with a debug panel showing intent, lead fields, and capture status.

### Option 2 — Terminal CLI

```bash
python main.py
```

Type messages at the `You:` prompt. Type `exit` to quit.

---

## Demo Walkthrough

Follow `demo_script.txt` for a full end-to-end lead qualification demo:

```
You:  Hi, tell me about your pricing.
Agent: [retrieves pricing from knowledge base]

You:  That sounds good, I want to try the Pro plan for my YouTube channel.
Agent: Detects high intent → asks for name

You:  My name is Thanujaa.
Agent: Asks for email

You:  thanu@example.com
Agent: Asks for platform (if not already extracted)

You:  YouTube
Agent: Calls mock_lead_capture() → "Lead captured successfully!"
```

---

## Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.9+ | Runtime |
| LangGraph | ≥ 0.2.40 | Stateful agent graph |
| LangChain | ≥ 0.3.0 | Agent orchestration primitives |
| Streamlit | ≥ 1.40.0 | Web chat interface |

---

## Production Deployment (WhatsApp / Webhook)

To deploy this agent to WhatsApp in production:

1. Wrap the LangGraph workflow in a **FastAPI** or **Flask** webhook endpoint
2. Connect a WhatsApp Business API provider (Meta Cloud API or Twilio)
3. Replace in-memory `ChatState` with **Redis** or a database for session persistence across restarts
4. Add input validation, retry logic, logging, and webhook signature verification

---

## Future Improvements

- [ ] Swap keyword intent classification for an LLM-based classifier
- [ ] Replace local JSON RAG with a vector database (FAISS / Chroma)
- [ ] Add WhatsApp or Slack webhook integration
- [ ] Persist lead capture to a real CRM (HubSpot, Salesforce)
- [ ] Add unit tests for each graph node

---

## Author

**Thanujaa TSK**
B.Tech CSE — VIT Chennai | Registration No: 24BCE5520
GitHub: [@thanujaa-5520](https://github.com/thanujaa-5520)

---

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.
