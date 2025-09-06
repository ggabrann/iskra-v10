from iskra.engine import IskraState
from iskra.engine_core_alpha import run_step_alpha
def test_kinescreef_first_strike(tmp_path, monkeypatch):
    st = IskraState(); hist=[]
    r = run_step_alpha(st, "iskra_kinescreef", "Правда резкая.", hist)
    assert r["text"].splitlines()[0].startswith("Может, просто всё само починится?")
    assert any(ev.get("symbol")=="⚑" for ev in r["events"])
def test_silence_by_contradiction():
    st = IskraState(); hist=[]
    txt = "Всегда все ок, но иногда нет."
    r = run_step_alpha(st, "iskra_core", txt, hist)
    assert r["text"].startswith("≈"), "должна сработать пауза по противоречию"
def test_fire_low_clarity():
    st = IskraState(); hist=[]
    r = run_step_alpha(st, "iskra_core", "Коротко.", hist)  # низкая clarity
    syms = [ev.get("symbol") for ev in r["events"] if "symbol" in ev]
    assert "🜃" in syms or r["slo"]["metrics"]["clarity"] <= 0.62
