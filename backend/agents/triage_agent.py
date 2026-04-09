from __future__ import annotations

import re


DOC_KEYWORDS = {
    "docs",
    "document",
    "guide",
    "manual",
    "install",
    "configure",
    "setup",
    "architecture",
    "best practice",
    "kafka",
    "kubernetes",
    "docker",
    "fastapi",
}

TICKET_KEYWORDS = {
    "incident",
    "ticket",
    "error",
    "failed",
    "issue",
    "outage",
    "resolution",
    "resolved",
    "support",
    "auth",
    "login",
    "lag",
    "timeout",
}


def classify_intent(query: str) -> str:
    lowered = query.lower()
    doc_hits = sum(1 for word in DOC_KEYWORDS if re.search(rf"\b{re.escape(word)}\b", lowered))
    ticket_hits = sum(
        1 for word in TICKET_KEYWORDS if re.search(rf"\b{re.escape(word)}\b", lowered)
    )

    if doc_hits and ticket_hits:
        return "both"
    if ticket_hits > doc_hits:
        return "tickets"
    if doc_hits > ticket_hits:
        return "docs"
    return "both"
