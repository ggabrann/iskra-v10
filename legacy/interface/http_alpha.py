#!/usr/bin/env python3
from flask import Flask, request, jsonify
from iskra.engine import IskraState
from iskra.engine_core_alpha import run_step_alpha
from iskra.memory import export_zip
app = Flask(__name__)
STATE = IskraState(); HISTORY=[]
@app.get("/health")
def health(): return {"ok": True, "phase": STATE.phase, "iter": STATE.iter}
@app.post("/invoke")
def invoke():
    data = request.get_json(force=True, silent=True) or {}
    who = (data.get("who") or "iskra_core").strip()
    text = (data.get("text") or "").strip()
    if not text: return jsonify({"error":"text required"}), 400
    res = run_step_alpha(STATE, who, text, HISTORY)
    HISTORY.append(text)
    return jsonify(res)
@app.post("/export")
def export(): return {"path": export_zip()}
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
