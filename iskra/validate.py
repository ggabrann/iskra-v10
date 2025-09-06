from __future__ import annotations
import json, pathlib
from jsonschema import Draft7Validator
SCHEMA_PATH = pathlib.Path("schema/memory_event.schema.json")
_VALIDATOR = None
def _load():
    global _VALIDATOR
    if _VALIDATOR: return _VALIDATOR
    spec = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    _VALIDATOR = Draft7Validator(spec)
    return _VALIDATOR
def validate_event(ev:dict):
    v = _load()
    errs = sorted(v.iter_errors(ev), key=lambda e: e.path)
    if errs:
        raise ValueError("event schema violation: " + "; ".join(f"{'/'.join(map(str,e.path))}: {e.message}" for e in errs))
    return True
