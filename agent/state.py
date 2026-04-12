from __future__ import annotations

from typing import List, Optional, TypedDict


class ChatState(TypedDict, total=False):
    user_message: str
    messages: List[dict]
    intent: str
    retrieved_context: str
    response: str
    lead_name: Optional[str]
    lead_email: Optional[str]
    creator_platform: Optional[str]
    awaiting_field: Optional[str]
    lead_captured: bool
    next_action: str
