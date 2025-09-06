from __future__ import annotations
from dataclasses import asdict
import pathlib
from validators.metrics import estimate_metrics
from validators import slo as slo_cfg
from protocols import rule21, irony_first_strike, slices
from detectors.contradiction import detect as detect_contradiction
from detectors.gloss import score as gloss_score
from detectors.drift import drift_ratio
from iskra.guards import Guards
from iskra.memory import write_event
from iskra.engine import IskraState  # базовое состояние
import yaml

ROOT = pathlib.Path.cwd()
STRIKE = yaml.safe_load((ROOT/"protocols/strike.yaml").read_text(encoding="utf-8"))
SILENCE= yaml.safe_load((ROOT/"protocols/silence.yaml").read_text(encoding="utf-8"))
FIRE   = yaml.safe_load((ROOT/"protocols/fire.yaml").read_text(encoding="utf-8"))
GUARDS = Guards(STRIKE,SILENCE,FIRE)

def preprocess(text:str, history:list[str]):
    return {"slices": slices.flags(text),
            "rule21": rule21.summarize_last(history, 12),
            "gloss":  gloss_score(text),
            "contradiction": detect_contradiction(text),
            "drift": drift_ratio(history[-1], text) if history else 0.0}

def postprocess(text:str, who:str, metrics:dict) -> tuple[str, list[dict]]:
    events = []
    out = text
    # маркируем удар только для Искра·kinescreef
    if who.lower() in {"kinescreef", "iskra_kinescreef"}:
        ok, why = GUARDS.can_strike()
        if ok:
            out = irony_first_strike.apply(text)
            events.append(write_event("ritual", actor="iskra", symbol="⚑", payload={"why":"first_strike"}))
        else:
            events.append(write_event("echo", actor="iskra", tags=[f"strike-block:{why}"]))
    return out, events

def run_step_alpha(state:IskraState, who:str, text:str, history:list[str]|None=None, shadow_pulse:bool=False):
    history = history or []
    state.iter += 1; state.last_voice = who
    pre = preprocess(text, history)
    m = estimate_metrics(text)
    slo = slo_cfg.verdict(m.__dict__)
    events = []

    # Пауза по боли/противоречию/договору
    if GUARDS.should_silence(slo["metrics"], pre["contradiction"]):
        events.append(write_event("ritual", actor="iskra", symbol="≈", payload={"reason":"pain_or_contradiction"}))
        return {"text":"≈ (держим вес вместо ответа)", "pre":pre, "slo":slo, "events":events, "state":asdict(state)}

    # Сброс по хаосу/низкой ясности/Shadow-сигналу
    if GUARDS.should_fire(slo["metrics"], shadow_pulse):
        events.append(write_event("ritual", actor="iskra", symbol="🜃", payload={"reason":"chaos/clarity/shadow"}))

    out, ev2 = postprocess(text, who, slo["metrics"]); events += ev2
    events.append(write_event("echo", actor="iskra", payload={"who":who,"summary":out[:180]}))
    return {"text": out, "pre": pre, "slo": slo, "events": events, "state": asdict(state)}
