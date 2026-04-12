from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LeadRecord:
    name: str
    email: str
    platform: str


def mock_lead_capture(name: str, email: str, platform: str) -> LeadRecord:
    print(f"Lead captured successfully: {name}, {email}, {platform}")
    return LeadRecord(name=name, email=email, platform=platform)
