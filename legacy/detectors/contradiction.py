from __future__ import annotations
import re
PATTERNS = [
    r"\b(и\s+да,\s+и\s+нет)\b",
    r"\b(всегда)\b.*\b(кроме|но)\b",
    r"\b(никогда)\b.*\b(если)\b"
]
RX = [re.compile(p, re.I | re.S) for p in PATTERNS]
def detect(text: str) -> bool:
    t = (text or "").strip()
    return any(rx.search(t) for rx in RX)
