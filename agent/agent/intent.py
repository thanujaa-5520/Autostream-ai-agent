from __future__ import annotations

import re
from typing import Dict


GREETING_KEYWORDS = {
    "hi", "hello", "hey", "good morning", "good afternoon", "good evening"
}

INQUIRY_KEYWORDS = {
    "price", "pricing", "plan", "plans", "cost", "feature", "features",
    "refund", "support", "resolution", "caption", "captions", "policy"
}

HIGH_INTENT_KEYWORDS = {
    "sign up", "signup", "buy", "purchase", "start", "get started", "try",
    "interested", "want pro", "want basic", "subscribe", "demo", "contact me"
}

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

PLATFORM_HINTS = {"youtube", "instagram", "tiktok", "linkedin", "facebook", "twitch"}


def extract_entities(text: str) -> Dict[str, str]:
    """Extract lead fields from free-form user input when possible."""
    lowered = text.lower().strip()
    entities: Dict[str, str] = {}

    email_match = EMAIL_RE.search(text)
    if email_match:
        entities["lead_email"] = email_match.group(0)

    for platform in PLATFORM_HINTS:
        if platform in lowered:
            entities["creator_platform"] = platform.title()
            break

    # Very lightweight name extraction patterns.
    name_patterns = [
        r"(?:my name is|i am|i'm)\s+([A-Za-z][A-Za-z\s'-]{1,40})",
        r"name\s*[:\-]\s*([A-Za-z][A-Za-z\s'-]{1,40})",
    ]
    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            entities["lead_name"] = match.group(1).strip().title()
            break

    return entities


def classify_intent(text: str) -> str:
    lowered = text.lower().strip()

    if any(keyword in lowered for keyword in HIGH_INTENT_KEYWORDS):
        return "high_intent_lead"

    if any(keyword in lowered for keyword in INQUIRY_KEYWORDS):
        return "product_or_pricing_inquiry"

    if any(keyword in lowered for keyword in GREETING_KEYWORDS):
        return "casual_greeting"

    # If the user provides contact details after earlier qualification, we treat it as lead progression.
    if EMAIL_RE.search(text) or any(platform in lowered for platform in PLATFORM_HINTS):
        return "high_intent_lead"

    return "product_or_pricing_inquiry"
