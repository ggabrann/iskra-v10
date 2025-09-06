from __future__ import annotations
import json, uuid, time, pathlib, zipfile
from iskra.validate import validate_event
ROOT = pathlib.Path.cwd()
def write_event(kind:str, actor:str="iskra", **kw) -> dict:
    ev = {
        "id": str(uuid.uuid4()),
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "kind": kind,
        "actor": actor,
        **kw
    }
    validate_event(ev)
    path = ROOT/"memory"/"events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.open("a", encoding="utf-8").write(json.dumps(ev, ensure_ascii=False)+"\n")
    return ev
def export_zip(out:str="memory_export.zip"):
    zpath = ROOT/out
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in (ROOT/"memory").glob("*"):
            z.write(p, p.relative_to(ROOT))
        for extra in [ROOT/"schema"/"memory_event.schema.json","config/slo.yaml"]:
            if extra.exists(): z.write(extra, extra.relative_to(ROOT))
    return str(zpath)
