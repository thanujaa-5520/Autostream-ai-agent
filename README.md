# AutoStream Social-to-Lead Agentic Workflow

This project implements a conversational AI agent for a fictional SaaS company called **AutoStream**, which offers automated video editing tools for content creators. The agent is designed to simulate a real business workflow rather than act as a simple chatbot.

## Features
- Intent identification for:
  - casual greeting
  - product or pricing inquiry
  - high-intent lead
- RAG-style answer generation using a **local JSON knowledge base**
- Memory/state across multiple turns
- Lead qualification workflow
- Mock tool execution using `mock_lead_capture(name, email, platform)`

## Project Structure
```bash
.
├── agent/
│   ├── graph.py
│   ├── intent.py
│   ├── rag.py
│   ├── state.py
│   └── tools.py
├── data/
│   └── knowledge.json
├── demo_script.txt
├── main.py
├── README.md
└── requirements.txt
```

## How to Run Locally
1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
2. Activate it:
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the agent:
   ```bash
   python main.py
   ```

## Architecture Explanation
I chose **LangGraph** because the assignment asks for an agent that can reason over multiple steps, preserve state across several turns, and trigger a tool only when business conditions are satisfied. LangGraph is a good fit for this because it models the agent as an explicit workflow graph, which makes the behavior easy to understand, test, and extend.

The graph in this project contains five major stages: **intent detection**, **retrieval**, **lead routing**, **response generation**, and **tool execution**. The first node classifies the user message into one of the required intent categories. If the message is informational, the flow moves to retrieval, where the system fetches relevant details from a local JSON knowledge base. If the message indicates strong buying intent, the workflow moves into lead routing, where the system checks whether the user’s name, email, and creator platform have all been collected.

State is managed through a shared `ChatState` object. This state stores conversation messages, detected intent, retrieved knowledge, pending fields, and captured lead information. Because the same state is passed through every node, the agent can remember details over 5–6 turns and avoid triggering the tool prematurely.

## WhatsApp Deployment Using Webhooks
To integrate this agent with WhatsApp in production, I would place the LangGraph workflow behind a backend API built with FastAPI or Flask. A WhatsApp Business API provider such as Meta Cloud API or Twilio would send incoming user messages to a webhook endpoint. The webhook would extract the sender ID, map it to a stored conversation state, pass the message into the LangGraph agent, and return the generated response back to WhatsApp through the provider’s messaging API.

The main production requirement is **session persistence**. Instead of storing state only in memory, I would store each user’s conversation state in Redis or a database. That ensures the agent remembers previous turns even if the backend restarts. I would also add validation, logging, retry handling, and authentication for secure webhook processing.

## Notes
- The knowledge base is stored locally in `data/knowledge.json`.
- Tool execution occurs only after all required lead fields are collected.
- This implementation is intentionally lightweight and easy to run for assignment/demo purposes.
