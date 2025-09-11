from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List, Optional, AsyncGenerator
import os, json, asyncio, datetime, pathlib

APP_TITLE = "Iskra Core"
BASE_DIR = pathlib.Path(os.getcwd())
DATA_DIR = BASE_DIR / "data"
GROWTH_DIR = BASE_DIR / "growth_nodes"
SNAP_DIR = BASE_DIR / "epochs" / "snapshots"
SYMBOLS_FILE = DATA_DIR / "symbols.json"
GROWTH_FILE = GROWTH_DIR / "growth.jsonl"
SLO_FILE = DATA_DIR / "slo_metrics.json"

for p in [DATA_DIR, GROWTH_DIR, SNAP_DIR]:
    p.mkdir(parents=True, exist_ok=True)

app = FastAPI(title=APP_TITLE)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

# ---- Simple in-process broadcaster for SSE ----
class Broadcaster:
    def __init__(self):
        self._subs: List[asyncio.Queue[str]] = []
        self._lock = asyncio.Lock()

    async def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue[str] = asyncio.Queue()
        async with self._lock:
            self._subs.append(q)
        return q

    async def unsubscribe(self, q: asyncio.Queue):
        async with self._lock:
            if q in self._subs:
                self._subs.remove(q)

    async def publish(self, event: Dict[str, Any]):
        data = json.dumps({"ts": datetime.datetime.utcnow().isoformat() + "Z", **event})
        async with self._lock:
            for q in list(self._subs):
                await q.put(data)

broadcaster = Broadcaster()

# ---- Models ----
class SymbolItems(BaseModel):
    # Either a dict mapping or a list of strings; both are supported
    symbols: Optional[Dict[str, Any]] = None
    items: Optional[List[str]] = None

class GrowthNode(BaseModel):
    # Accept any shape; minimally store text field
    text: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None

class SnapshotReq(BaseModel):
    meta: Optional[Dict[str, Any]] = None

# ---- Utils ----
def _read_json(path: pathlib.Path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default

def _write_json(path: pathlib.Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

# ---- Basic health ----
@app.get("/")
async def root():
    return {"iskra": "alive"}

@app.get("/health")
async def health():
    return {"ok": True}

# ---- Symbols API (MCP-ish) ----
@app.get("/symbols/list")
async def symbols_list():
    data = _read_json(SYMBOLS_FILE, {})
    return {"symbols": data}

@app.post("/symbols/upsert")
async def symbols_upsert(body: SymbolItems):
    current = _read_json(SYMBOLS_FILE, {})
    if body.symbols:
        current.update(body.symbols)
    if body.items:
        for s in body.items:
            current.setdefault(s, True)
    _write_json(SYMBOLS_FILE, current)
    await broadcaster.publish({"type": "symbols.upsert", "size": len(current)})
    return {"ok": True, "size": len(current)}

# ---- Growth nodes ----
@app.post("/growth/add")
async def growth_add(node: GrowthNode):
    GROWTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "text": node.text,
        "payload": node.payload or {},
    }
    with GROWTH_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    await broadcaster.publish({"type": "growth.add", "text": node.text})
    return {"ok": True}

# ---- Epoch snapshot ----
@app.post("/epoch/snapshot")
async def epoch_snapshot(req: SnapshotReq):
    # read current state (symbols + growth size) and persist snapshot
    symbols = _read_json(SYMBOLS_FILE, {})
    growth_count = 0
    if GROWTH_FILE.exists():
        with GROWTH_FILE.open("r", encoding="utf-8") as f:
            for _ in f:
                growth_count += 1
    snap = {
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "meta": req.meta or {},
        "symbols_count": len(symbols),
        "growth_count": growth_count,
    }
    snap_name = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ") + ".json"
    snap_path = SNAP_DIR / snap_name
    _write_json(snap_path, snap)
    await broadcaster.publish({"type": "epoch.snapshot", "file": str(snap_path)})
    return {"ok": True, "file": f"epochs/snapshots/{snap_name}", "data": snap}

# ---- SLO report (toy aggregation) ----
@app.get("/slo/report")
async def slo_report():
    # You can compute from real metrics; for now we derive from volumes
    symbols = _read_json(SYMBOLS_FILE, {})
    growth_count = 0
    if GROWTH_FILE.exists():
        with GROWTH_FILE.open("r", encoding="utf-8") as f:
            for _ in f:
                growth_count += 1
    total = max(1, len(symbols) + growth_count)
    report = {
        "clarity": round(len(symbols) / total, 4),
        "drift": round(max(0.0, (growth_count - len(symbols)) / total), 4),
        "pain": 0.0,  # placeholder
        "echo": 0.0,  # placeholder
        "symbols": len(symbols),
        "growth": growth_count,
    }
    _write_json(SLO_FILE, report)
    await broadcaster.publish({"type": "slo.report", "report": report})
    return report

# ---- SSE ----
async def event_generator(q: asyncio.Queue[str]) -> AsyncGenerator[bytes, None]:
    try:
        # initial hello
        yield f"data: {json.dumps({'hello': APP_TITLE})}\n\n".encode("utf-8")
        while True:
            data = await q.get()
            yield f"data: {data}\n\n".encode("utf-8")
    except asyncio.CancelledError:
        raise
    finally:
        await broadcaster.unsubscribe(q)

@app.get("/sse")
async def sse(request: Request):
    q = await broadcaster.subscribe()
    return StreamingResponse(event_generator(q), media_type="text/event-stream")
