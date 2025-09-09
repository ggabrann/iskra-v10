from __future__ import annotations
import yaml, pathlib
CFG = {"thresholds":{"clarity_min":0.80,"drift_max":0.30}}
def load():
    p = pathlib.Path("config/slo.yaml")
    if p.exists():
        try:
            return yaml.safe_load(p.read_text(encoding="utf-8")) or CFG
        except Exception:
            return CFG
    return CFG
def verdict(metrics:dict)->dict:
    cfg = load().get("thresholds", {})
    cm, dm = float(cfg.get("clarity_min",0.8)), float(cfg.get("drift_max",0.3))
    ok = (metrics.get("clarity",0) >= cm) and (metrics.get("drift",1) <= dm)
    return {"ok": ok, "thresholds":{"clarity_min":cm, "drift_max":dm}, "metrics": metrics}
