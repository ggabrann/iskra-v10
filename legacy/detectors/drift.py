from __future__ import annotations
import re
def _tokens(s:str)->set[str]:
    return set(re.findall(r"[a-zA-Zа-яА-Я0-9]{3,}", s.lower()))
def jaccard(a:set[str], b:set[str])->float:
    if not a and not b: return 1.0
    u = a|b; i = a&b
    return len(i)/len(u) if u else 0.0
def drift_ratio(prev:str, cur:str)->float:
    A, B = _tokens(prev or ""), _tokens(cur or "")
    sim = jaccard(A,B)
    return max(0.0, 1.0 - sim)  # 0 – без дрейфа, 1 – полный разрыв
