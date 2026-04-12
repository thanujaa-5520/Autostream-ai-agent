from __future__ import annotations

from pathlib import Path
from typing import Dict

from langgraph.graph import END, StateGraph

from agent.intent import classify_intent, extract_entities
from agent.rag import LocalKnowledgeBase
from agent.state import ChatState
from agent.tools import mock_lead_capture


BASE_DIR = Path(__file__).resolve().parent.parent
KB = LocalKnowledgeBase(str(BASE_DIR / "data" / "knowledge.json"))


def intent_node(state: ChatState) -> ChatState:
    user_message = state.get("user_message", "")
    state["intent"] = classify_intent(user_message)

    # Pull any lead details from current message.
    extracted = extract_entities(user_message)
    for key, value in extracted.items():
        state[key] = value

    return state


def retrieval_node(state: ChatState) -> ChatState:
    user_message = state.get("user_message", "")
    state["retrieved_context"] = KB.retrieve(user_message)
    state["next_action"] = None
    return state


def lead_router_node(state: ChatState) -> ChatState:
    lead_name = state.get("lead_name")
    lead_email = state.get("lead_email")
    creator_platform = state.get("creator_platform")

    if not lead_name:
        state["awaiting_field"] = "lead_name"
        state["next_action"] = "ask_name"
    elif not lead_email:
        state["awaiting_field"] = "lead_email"
        state["next_action"] = "ask_email"
    elif not creator_platform:
        state["awaiting_field"] = "creator_platform"
        state["next_action"] = "ask_platform"
    else:
        state["awaiting_field"] = None
        state["next_action"] = "capture_lead"

    return state


def response_node(state: ChatState) -> ChatState:
    intent = state.get("intent", "product_or_pricing_inquiry")
    context = state.get("retrieved_context", "")
    next_action = state.get("next_action")

    if next_action == "ask_name":
        state["response"] = (
            "Great choice — I can help you get started with AutoStream. "
            "Before I register your interest, may I have your name?"
        )
        return state

    if next_action == "ask_email":
        state["response"] = "Thanks! Please share your email address so I can capture your lead."
        return state

    if next_action == "ask_platform":
        state["response"] = (
            "Got it. Which creator platform do you mainly use — YouTube, Instagram, TikTok, or something else?"
        )
        return state

    if intent == "casual_greeting":
        state["response"] = (
            "Hi! I can help with AutoStream pricing, features, policies, or getting you started on a plan."
        )
        return state

    if intent == "high_intent_lead":
        # If details are still missing, lead_router_node will decide what to ask next.
        # This message is only used when high intent is detected but no immediate question is needed.
        state["response"] = (
            "Awesome — it sounds like you're interested in trying AutoStream. "
            "I'll just collect a few details to get this set up for you."
        )
        return state

    # Inquiry response from local knowledge base.
    state["response"] = (
        "Here’s what I found from the AutoStream knowledge base:\n\n"
        f"{context}\n\n"
        "If you'd like, I can also help you choose between Basic and Pro."
    )
    return state


def tool_node(state: ChatState) -> ChatState:
    # Capture only once, and only when all three fields are present.
    if (
        state.get("next_action") == "capture_lead"
        and not state.get("lead_captured", False)
        and state.get("lead_name")
        and state.get("lead_email")
        and state.get("creator_platform")
    ):
        record = mock_lead_capture(
            name=state["lead_name"],
            email=state["lead_email"],
            platform=state["creator_platform"],
        )
        state["lead_captured"] = True
        state["next_action"] = None
        state["awaiting_field"] = None
        state["response"] = (
            "Lead captured successfully! "
            f"Recorded: {record.name}, {record.email}, {record.platform}. "
            "Our team can now follow up with you."
        )
    return state


def route_after_intent(state: ChatState) -> str:
    has_partial_lead = any(
        [
            state.get("awaiting_field"),
            state.get("lead_name"),
            state.get("lead_email"),
            state.get("creator_platform"),
        ]
    ) and not state.get("lead_captured", False)

    if state.get("intent") == "high_intent_lead" or has_partial_lead:
        return "lead_router"
    return "retrieval"


def route_after_lead_router(state: ChatState) -> str:
    if state.get("next_action") == "capture_lead":
        return "tool"
    return "respond"


def build_graph():
    graph = StateGraph(ChatState)

    graph.add_node("intent", intent_node)
    graph.add_node("retrieval", retrieval_node)
    graph.add_node("lead_router", lead_router_node)
    graph.add_node("respond", response_node)
    graph.add_node("tool", tool_node)

    graph.set_entry_point("intent")

    graph.add_conditional_edges(
        "intent",
        route_after_intent,
        {
            "retrieval": "retrieval",
            "lead_router": "lead_router",
        },
    )
    graph.add_edge("retrieval", "respond")
    graph.add_conditional_edges(
        "lead_router",
        route_after_lead_router,
        {
            "respond": "respond",
            "tool": "tool",
        },
    )
    graph.add_edge("respond", END)
    graph.add_edge("tool", END)

    return graph.compile()


class AutoStreamAgent:
    def __init__(self) -> None:
        self.app = build_graph()
        self.state: ChatState = {
            "messages": [],
            "lead_captured": False,
            "lead_name": None,
            "lead_email": None,
            "creator_platform": None,
            "awaiting_field": None,
        }

    def chat(self, user_message: str) -> Dict[str, str]:
        self.state["user_message"] = user_message
        self.state.setdefault("messages", []).append({"role": "user", "content": user_message})

        # If we were waiting on a specific field, treat the message as a direct answer.
        awaiting = self.state.get("awaiting_field")
        if awaiting and user_message.strip():
            direct_entities = extract_entities(user_message)

            if awaiting == "lead_name":
                if "lead_name" in direct_entities:
                    self.state["lead_name"] = direct_entities["lead_name"]
                else:
                    self.state["lead_name"] = user_message.strip().title()

            elif awaiting == "lead_email":
                if "lead_email" in direct_entities:
                    self.state["lead_email"] = direct_entities["lead_email"]
                else:
                    self.state["lead_email"] = user_message.strip()

            elif awaiting == "creator_platform":
                if "creator_platform" in direct_entities:
                    self.state["creator_platform"] = direct_entities["creator_platform"]
                else:
                    self.state["creator_platform"] = user_message.strip().title()

        self.state = self.app.invoke(self.state)
        reply = self.state.get("response", "Sorry, something went wrong.")
        self.state.setdefault("messages", []).append({"role": "assistant", "content": reply})
        return {
            "intent": self.state.get("intent", "unknown"),
            "response": reply,
            "lead_name": self.state.get("lead_name") or "",
            "lead_email": self.state.get("lead_email") or "",
            "creator_platform": self.state.get("creator_platform") or "",
            "lead_captured": str(self.state.get("lead_captured", False)),
        }
