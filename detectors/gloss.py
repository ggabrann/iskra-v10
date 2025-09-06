from __future__ import annotations
GENERIC = {"в целом ок","как обычно","всё решено","нормально","как-нибудь потом","всё понятно"}
def score(text:str) -> float:
    t = (text or "").lower()
    hits = sum(1 for g in GENERIC if g in t)
    return min(1.0, hits * 0.4)
