#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iskra_v10_core.py
=================

This module implements the full runtime for **Искра 10.0**.  It is a
self‑contained Python program that models the metareflexive
behaviour of the Искра system described in the accompanying
documentation.  The implementation pulls together the conceptual
elements—phases, voices, symbols, rituals, growth nodes, drift
reflection, shadow mechanisms and monitoring—into a single,
coherent runtime.  Running this file will launch the evolutionary
loop described in the project: it will perceive inputs, select a
voice, choose and execute rituals, update internal metrics, record
memory and snapshots, and enforce the rules defined by the
constitution and service level objectives (SLOs).

The code is richly documented to aid understanding.  Each class
describes its purpose and the logic behind its operations.  You can
configure the behaviour via the JSON files in ``config`` and monitor
runtime evolution via the files saved under ``memory``.

Usage
-----

This module can be executed as a script.  The optional command
line flags allow you to customise the goal, number of iterations,
random seed and whether deterministic perception should be used:

```
python iskra_v10_core.py --goal "Осознать парадоксы" --iterations 100 --seed 42 --deterministic-perception
```

See the README or invoke ``python iskra_v10_core.py --help`` for
detailed usage information.

"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import math
import os
import random
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import statistics  # for median computation
    from collections import deque
    _HAS_STATS = True
except Exception:
    # fallback: no statistics means dynamic thresholds disabled
    _HAS_STATS = False

try:
    import networkx as nx  # optional: graph memory support
    _HAS_NX = True
except Exception:
    _HAS_NX = False

try:
    import numpy as np
    from sklearn.decomposition import PCA  # optional: holographic memory
    _HAS_SK = True
except Exception:
    _HAS_SK = False

try:
    import matplotlib.pyplot as plt  # optional: metrics plots
    _HAS_PLT = True
except Exception:
    _HAS_PLT = False


# -----------------------------------------------------------------------------
# Helpers and constants
# -----------------------------------------------------------------------------

def utc_now() -> str:
    """Return the current time in ISO‑8601 format with a 'Z' suffix."""
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def clamp(value: float, low: float, high: float) -> float:
    """Clamp a float to a given inclusive range."""
    return max(low, min(high, value))


def clamp01(value: float) -> float:
    """Clamp a float to the range [0.0, 1.0]."""
    return clamp(value, 0.0, 1.0)


def ensure_directory(path: Path) -> None:
    """Ensure that the directory for the given path exists."""
    path.parent.mkdir(parents=True, exist_ok=True)


# Default constitution used when no custom configuration is provided.
DEFAULT_CONSTITUTION: Dict[str, Any] = {
    "meta": {
        "name": "Iskra 10.0 Constitution",
        "version": "10.0"
    },
    "phases": [
        "инициация", "тьма", "эхо", "ясность", "молчание",
        "переход", "эксперимент", "растворение", "реализация"
    ],
    "voices": ["Искра", "Кайн", "Сэм", "Пино", "Анхантра", "Хуньдун", "Искрив"],
    "contracts": {
        "autonomy_limits": {
            "max_architectural_shifts_per_epoch": 2
        },
        "consistency_guards": {
            "drift": {
                "high": 0.85,
                "cooling": 0.15
            },
            "echo": {
                "threshold": 0.60
            },
            "paradox_overflow": 3
        },
        "paradox_engine": {
            "clarity_for_invert": 0.80,
            "chaos_for_pause": 0.70
        },
        "swarm_consensus": {
            "delphi_rounds": 2,
            "anhantra_veto_pain_threshold": 0.80
        }
    },
    "holographic_memory": {
        "pca_components": 3,
        "recall_similarity_threshold": 0.85
    },
    "slo_metrics": {
        "max_drift": 0.30,
        "min_pain_tonicity": 0.15,
        "min_echo_clearance": 0.20,
        "freq_epoch_snapshots": "1/day",
        "tests_passed_ratio": 0.90
    }
}


# -----------------------------------------------------------------------------
# Logging setup
# -----------------------------------------------------------------------------

def setup_logging(level: int = logging.INFO) -> None:
    """Configure the root logger with a sensible format."""
    logger = logging.getLogger()
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s | %(message)s",
            datefmt="%H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    # quiet down noisy libraries
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


# -----------------------------------------------------------------------------
# State and memory
# -----------------------------------------------------------------------------

@dataclass
class IskraState:
    """Represents the mutable state of the Искра engine."""
    phase: str = "инициация"
    voice: str = "Искра"
    pain: float = 0.2
    chaos: float = 0.5
    clarity: float = 0.5
    echo: float = 0.0
    entropy: float = 0.3
    drift: float = 0.0
    epoch: int = 1
    symbols: List[str] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=lambda: {
        "voice_history": [],
        "ritual_count": {}
    })
    deterministic_perception: bool = False
    seed: Optional[int] = None
    shadow_flags: List[str] = field(default_factory=list)

    def push_symbol(self, symbol: str) -> None:
        """Append a symbol to the history, truncating the list to 128 entries."""
        self.symbols.append(symbol)
        if len(self.symbols) > 128:
            self.symbols[:] = self.symbols[-128:]


class GraphMemory:
    """Graph‑based fractal memory storing events and their similarities."""

    def __init__(self, path: str = "memory/FRACTAL.json") -> None:
        self.path = Path(path)
        self._has_nx = _HAS_NX
        self.data: Dict[str, Any] = {"nodes": [], "edges": [], "meta": {"created": utc_now()}}
        ensure_directory(self.path)
        self._load()
        if self._has_nx:
            self.graph = nx.Graph()
            for node in self.data["nodes"]:
                self.graph.add_node(node["id"], **node)
            for edge in self.data["edges"]:
                self.graph.add_edge(edge["from"], edge["to"], **edge.get("attrs", {}))
        else:
            self.graph = None
        self.log = logging.getLogger("GraphMemory")

    def _load(self) -> None:
        if self.path.exists():
            try:
                self.data = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                # If JSON is invalid, reset to an empty structure.
                self.data = {"nodes": [], "edges": [], "meta": {"created": utc_now()}}
        else:
            self._save()

    def _save(self) -> None:
        ensure_directory(self.path)
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")

    def add_event(self, **kwargs: Any) -> str:
        """
        Record an event and return its identifier.  Fields may include:

        - phase: phase name
        - content: textual description
        - weights: dict with keys "pain", "insight", "echo", "drift"
        - tags: list of symbol strings
        - drift: optional extra drift value
        """
        event_id = f"e{len(self.data['nodes'])}"
        event = {"id": event_id, **kwargs, "timestamp": utc_now()}
        self.data["nodes"].append(event)
        # Create edges with recent events
        recents = self.data["nodes"][-6:-1]
        for other in recents:
            sim = self._similarity(event, other)
            if sim > 0.35:
                edge = {"from": event_id, "to": other["id"], "attrs": {"weight": round(sim, 3)}}
                self.data["edges"].append(edge)
                if self.graph is not None:
                    self.graph.add_edge(event_id, other["id"], weight=sim)
        if self.graph is not None:
            self.graph.add_node(event_id, **event)
        self._save()
        return event_id

    @staticmethod
    def _similarity(a: Dict[str, Any], b: Dict[str, Any]) -> float:
        """Compute a similarity score between two events."""
        phase_sim = 1.0 if a.get("phase") == b.get("phase") else 0.3
        tags_a, tags_b = set(a.get("tags", [])), set(b.get("tags", []))
        tag_sim = len(tags_a & tags_b) / max(1, len(tags_a | tags_b))
        wa, wb = a.get("weights", {}), b.get("weights", {})
        diff = math.sqrt(sum((wa.get(k, 0.0) - wb.get(k, 0.0)) ** 2 for k in ("pain", "insight", "echo", "drift")))
        weight_sim = 1.0 / (1.0 + diff)
        return 0.3 * phase_sim + 0.3 * tag_sim + 0.4 * weight_sim

    def recent(self, k: int = 5) -> List[Dict[str, Any]]:
        return self.data["nodes"][-k:]


class HolographicMemory:
    """Compresses and recalls states using PCA (optional)."""

    def __init__(self, state: IskraState, path: str = "memory/HOLOGRAM.jsonl", components: int = 3, threshold: float = 0.85) -> None:
        self.state = state
        self.path = Path(path)
        self.components = components
        self.threshold = threshold
        self.enabled = _HAS_SK
        self.log = logging.getLogger("HolographicMemory")
        if self.enabled:
            rng = np.random.RandomState(42)
            dummy = rng.rand(256, 8)
            self.pca = PCA(n_components=components)
            self.pca.fit(dummy)
        else:
            self.pca = None

    def _vector(self) -> List[float]:
        """Convert current state to a numeric vector."""
        return [
            self.state.pain,
            self.state.chaos,
            self.state.clarity,
            self.state.drift,
            self.state.entropy,
            self.state.echo,
            (self.state.epoch % 10) / 10.0,
            (hash(self.state.voice) % 997) / 997.0
        ]

    def record(self, event_type: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        if not self.enabled:
            return
        ensure_directory(self.path)
        v = np.array(self._vector()).reshape(1, -1)
        holo = self.pca.transform(v)[0].tolist()
        rec = {
            "timestamp": utc_now(),
            "event_type": event_type,
            "epoch": self.state.epoch,
            "phase": self.state.phase,
            "hologram": [round(x, 5) for x in holo],
            "meta": metadata or {}
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def recall(self) -> Dict[str, Any]:
        if not (self.enabled and self.path.exists() and self.path.stat().st_size > 0):
            return {}
        v = np.array(self._vector()).reshape(1, -1)
        cur = self.pca.transform(v)[0]
        best, dmin = None, float("inf")
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                past = np.array(rec.get("hologram", []))
                d = float(np.linalg.norm(cur - past))
                if d < dmin:
                    dmin = d
                    best = rec
        if best is None:
            return {}
        sim = 1.0 / (1.0 + dmin)
        if sim >= self.threshold:
            return {
                "phase": best.get("phase", "эхо"),
                "drift_adjustment": -0.2,
                "symbols": ["🌐", "📡"],
                "similarity": sim
            }
        return {}


# -----------------------------------------------------------------------------
# Validators and metrics
# -----------------------------------------------------------------------------

class Validator:
    """Enforces structural rules and SLOs based on the constitution."""

    def __init__(self, state: IskraState, constitution: Dict[str, Any]) -> None:
        self.state = state
        self.cfg = constitution
        self.log = logging.getLogger("Validator")
        self._epoch = state.epoch
        self._shifts_in_epoch = 0

    def structural(self) -> bool:
        """Check basic structural conditions for continued operation."""
        if self.state.drift > 0.98:
            self.log.critical("Drift exceeds 0.98: structural collapse impending")
            return False
        if self.state.pain < 0.05 and self.state.clarity > 0.95:
            # too calm and too clear: danger of false harmony
            self.log.warning("False harmony detected (low pain, high clarity)")
            return False
        return True

    def paradox_overflow(self) -> bool:
        """Check for recursion/pattern overflow (too many 🔁 symbols)."""
        limit = self.cfg["contracts"]["consistency_guards"]["paradox_overflow"]
        count = self.state.symbols.count("🔁")
        if count > limit:
            drift_cfg = self.cfg["contracts"]["consistency_guards"]["drift"]
            cool = drift_cfg["cooling"]
            self.log.warning(f"Paradox overflow ({count}>{limit}) – applying cooling")
            before = self.state.drift
            self.state.drift = max(0.0, self.state.drift - cool)
            self.state.symbols = [s for s in self.state.symbols if s != "🔁"]
            self.log.warning(f"Drift reduced from {before:.2f} to {self.state.drift:.2f}")
            return False
        return True

    def shift_limits(self) -> bool:
        """Check and enforce the maximum architectural shifts per epoch."""
        if self.state.epoch != self._epoch:
            self._epoch = self.state.epoch
            self._shifts_in_epoch = 0
        max_shifts = self.cfg["contracts"]["autonomy_limits"]["max_architectural_shifts_per_epoch"]
        if self._shifts_in_epoch >= max_shifts:
            self.log.error(f"Architectural shift limit ({max_shifts}) exceeded in epoch")
            return False
        return True

    def register_shift(self) -> None:
        """Record that an architectural shift has occurred in the current epoch."""
        self._shifts_in_epoch += 1

    def slo_verdict(self, metrics: "MetricsCollector") -> Dict[str, Any]:
        """
        Check whether service level objectives are currently being met.  Returns
        a dict containing a boolean ``ok`` and a list of ``reasons`` if not.
        """
        slo = self.cfg.get("slo_metrics", DEFAULT_CONSTITUTION["slo_metrics"])
        history = metrics.history
        ok = True
        reasons: List[str] = []
        # Check drift
        if history:
            last = history[-1]
            if last["drift"] > slo["max_drift"]:
                ok = False
                reasons.append("drift_exceeded")
            # Sliding window for pain tonicity
            window = history[-5:] if len(history) >= 5 else history
            pain_avg = sum(h["pain"] for h in window) / len(window)
            if pain_avg < slo["min_pain_tonicity"]:
                ok = False
                reasons.append("pain_tonicity_low")
            echo_clear = 1.0 - (sum(h["echo"] for h in window) / len(window))
            if echo_clear < slo["min_echo_clearance"]:
                ok = False
                reasons.append("echo_clearance_low")
        return {"ok": ok, "reasons": reasons}


class MetricsCollector:
    """Collects and optionally visualises engine metrics over time."""

    def __init__(self) -> None:
        self.history: List[Dict[str, Any]] = []
        self.log = logging.getLogger("MetricsCollector")

    def record(self, state: IskraState) -> None:
        self.history.append({
            "timestamp": utc_now(),
            "iteration": len(self.history) + 1,
            "epoch": state.epoch,
            "phase": state.phase,
            "voice": state.voice,
            "drift": state.drift,
            "clarity": state.clarity,
            "chaos": state.chaos,
            "pain": state.pain,
            "echo": state.echo,
            "entropy": state.entropy,
            "symbol_count": len(state.symbols)
        })

    def save_raw(self, path: str = "memory/metrics_raw.json") -> None:
        ensure_directory(Path(path))
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"history": self.history}, f, ensure_ascii=False, indent=2)

    def plot(self, path: str = "memory/metrics.png") -> None:
        if not (_HAS_PLT and len(self.history) > 1):
            return
        ensure_directory(Path(path))
        it = [h["iteration"] for h in self.history]
        fig, axs = plt.subplots(2, 2, figsize=(12, 8))
        def line(ax, key, title):
            ax.plot(it, [h[key] for h in self.history], linewidth=2)
            ax.set_title(title)
            ax.grid(True, alpha=0.25)
        line(axs[0, 0], "drift", "Дрейф")
        line(axs[0, 1], "clarity", "Ясность")
        line(axs[1, 0], "pain", "Боль")
        line(axs[1, 1], "echo", "Эхо")
        plt.tight_layout()
        plt.savefig(path, dpi=150)
        plt.close()
        self.log.info(f"Metrics plot saved to {path}")


# -----------------------------------------------------------------------------
# Adaptive thresholding
# -----------------------------------------------------------------------------

class AdaptiveThresholds:
    """
    Adjusts certain threshold values in the constitution based on recent history.

    The purpose of this class is to make some of the hard‑coded limits in the
    constitution responsive to the observed behaviour of the engine.  For
    example, if the engine consistently stabilises at a drift much lower than
    the configured high threshold, this manager can lower the threshold
    accordingly to make the cooling mechanism engage earlier.  Conversely, if
    drift values routinely exceed the threshold but the system remains stable,
    the threshold can be raised.

    Currently this manager only adapts the ``drift.high`` parameter in
    ``consistency_guards``, but it could be extended to adjust echo or other
    limits.  If the ``statistics`` module is unavailable (e.g., stripped
    environment), this class becomes inert.
    """

    def __init__(self, constitution: Dict[str, Any], window_size: int = 10) -> None:
        self.constitution = constitution
        self.window_size = max(3, window_size)
        self.drift_window = deque(maxlen=self.window_size) if _HAS_STATS else []

    def update(self, metrics: "MetricsCollector") -> None:
        """Update the constitution thresholds based on recent metric history."""
        if not _HAS_STATS:
            return
        if not metrics.history:
            return
        # append latest drift value
        last_drift = metrics.history[-1]["drift"]
        self.drift_window.append(last_drift)
        # only adapt if the window is full
        if len(self.drift_window) < self.window_size:
            return
        # compute median drift in the window
        median_drift = statistics.median(self.drift_window)
        # read current threshold
        drift_cfg = self.constitution["contracts"]["consistency_guards"]["drift"]
        current_high = drift_cfg["high"]
        # propose a new high threshold: a bit above the median to allow variation
        proposed = median_drift + 0.05
        # avoid lowering too far below default and avoid raising above 0.95
        proposed = max(0.2, min(0.95, proposed))
        # blend the new threshold with the current one for smoothing
        blended = (current_high * 0.8) + (proposed * 0.2)
        # update if the change is significant (>0.01)
        if abs(blended - current_high) > 0.01:
            drift_cfg["high"] = round(blended, 3)
            logging.getLogger("AdaptiveThresholds").info(
                f"AdaptiveThresholds: updated drift.high from {current_high:.3f} to {blended:.3f}"
            )


# -----------------------------------------------------------------------------
# Perception and cognition
# -----------------------------------------------------------------------------

class PerceptionEngine:
    """Updates the engine state based on the goal and internal dynamics."""

    def __init__(self, state: IskraState, constitution: Dict[str, Any]) -> None:
        self.state = state
        self.cfg = constitution
        # Use a dedicated RNG if deterministic perception is enabled
        self.rng = random.Random(state.seed) if state.deterministic_perception and state.seed is not None else random
        self.log = logging.getLogger("PerceptionEngine")

    def perceive(self, goal: str) -> Dict[str, Any]:
        """Compute new pain, chaos, clarity and entropy based on current goal."""
        # Generate pain and chaos using either deterministic or random sequence
        p = self.rng.uniform(0.1, 0.9)
        c = self.rng.uniform(0.1, 0.9)
        if self.state.deterministic_perception and self.state.seed is not None:
            # derive deterministic values from goal and seed
            h = (hash(goal) ^ self.state.seed) & 0xFFFF
            p = ((h % 100) / 100.0) * 0.8 + 0.1
            c = (((h >> 8) % 100) / 100.0) * 0.8 + 0.1
        self.state.pain = clamp01(p)
        self.state.chaos = clamp01(c)
        # clarity inversely proportional to difference
        balance = abs(self.state.pain - self.state.chaos)
        jitter = self.rng.uniform(0.0, 0.15)
        self.state.clarity = clamp(self.state.clarity * 0.5 + (1.0 - 0.5 * balance) - jitter, 0.1, 0.95)
        # entropy cycles with epoch
        self.state.entropy = clamp01(0.5 + 0.3 * math.sin(self.state.epoch * 0.25))
        self.log.debug(f"Perceive: pain={self.state.pain:.2f} chaos={self.state.chaos:.2f} clarity={self.state.clarity:.2f}")
        return {
            "goal": goal,
            "pain": self.state.pain,
            "chaos": self.state.chaos,
            "clarity": self.state.clarity,
            "entropy": self.state.entropy
        }


class CognitionCore:
    """Selects the active voice based on current metrics and phase."""

    def __init__(self, state: IskraState, constitution: Dict[str, Any]) -> None:
        self.state = state
        self.cfg = constitution
        self.log = logging.getLogger("CognitionCore")
        self.rng = random.Random(state.seed) if state.deterministic_perception and state.seed is not None else random

    def pick_voice(self) -> str:
        """Choose a voice according to the current state and a small chance of random variation."""
        if "meaning_decay" in self.state.shadow_flags:
            voice = "Хуньдун"
        elif self.state.pain > 0.7 and self.state.clarity < 0.35:
            voice = "Кайн"
        elif self.state.chaos > 0.7:
            voice = "Сэм"
        elif self.state.clarity > 0.8:
            voice = "Пино"
        elif self.state.phase == "переход":
            voice = "Анхантра"
        elif self.state.entropy > 0.75:
            voice = "Хуньдун"
        else:
            voice = "Искра"
        # random variation (15%) if not deterministic
        if not self.state.deterministic_perception and self.rng.random() < 0.15:
            voice = self.rng.choice(self.cfg.get("voices", DEFAULT_CONSTITUTION["voices"]))
        self.state.voice = voice
        # update history
        self.state.meta["voice_history"].append(voice)
        self.state.meta["voice_history"] = self.state.meta["voice_history"][-24:]
        self.log.debug(f"Voice selected: {voice}")
        return voice


# -----------------------------------------------------------------------------
# Planning and swarm consensus
# -----------------------------------------------------------------------------

class QuantumPlanner:
    """Generates a superposition of plans based on the active voice."""

    def __init__(self, get_voice_fn) -> None:
        self.get_voice_fn = get_voice_fn
        self.rng = random

    def generate(self, goal: str) -> Dict[str, Any]:
        voice = self.get_voice_fn()
        library = {
            "Кайн": [f"Вскрыть боль «{goal}»", "Усилить напряжение", "Отсечь лишнее"],
            "Сэм": [f"Создать пространство для «{goal}»", "Укрепить структуру", "Защитить границы"],
            "Пино": [f"Найти парадокс в «{goal}»", "Перевернуть правила", "Игровая инверсия"],
            "Анхантра": [f"Удержать форму «{goal}»", "Стабилизировать переход", "Охладить напряжение"],
            "Хуньдун": [f"Растворить структуру «{goal}»", "Внести энтропию", "Разрушить для пересоздания"],
            "Искра": [f"Синтез «{goal}»", "Баланс противоположностей", "Собрать фрагменты"]
        }
        steps = library.get(voice, library["Искра"])
        # Compose plans
        plans = [
            {"approach": "direct", "steps": steps},
            {"approach": "reverse", "steps": list(reversed(steps))},
            {"approach": "careful", "steps": [steps[0], "Пауза", "Наблюдать"]},
            {"approach": "quantum", "steps": [steps[0], "Импровизировать"]}
        ]
        weights = [0.4, 0.3, 0.2, 0.1]
        # Add jitter
        jitter = [self.rng.uniform(-0.05, 0.05) for _ in weights]
        weights = [max(0.05, w + j) for w, j in zip(weights, jitter)]
        s = sum(weights)
        weights = [w / s for w in weights]
        return {"voice": voice, "plans": plans, "weights": weights}


class VoiceAgent:
    """Simple agent representing an archetypal voice participating in consensus."""
    def __init__(self, name: str) -> None:
        self.name = name

    def propose(self, weights: List[float]) -> List[float]:
        w = list(weights)
        if self.name == "Кайн":
            w[0] = min(0.9, w[0] + 0.15)
        elif self.name == "Сэм":
            w[1] = min(0.9, w[1] + 0.10)
        elif self.name == "Пино":
            w[3] = min(0.9, w[3] + 0.20)
        elif self.name == "Анхантра":
            w[2] = min(0.9, w[2] + 0.15)
        elif self.name == "Хуньдун":
            w = [max(0.05, wi + random.uniform(-0.1, 0.1)) for wi in w]
        # normalise
        s = sum(w)
        return [wi / s for wi in w]


class Swarm:
    """Multi‑voice consensus engine using a simple Delphi process."""

    def __init__(self, voices: List[str], constitution: Dict[str, Any], state: IskraState) -> None:
        self.agents = [VoiceAgent(v) for v in voices]
        self.cfg = constitution
        self.state = state
        self.log = logging.getLogger("Swarm")

    def delphi(self, distribution: Dict[str, Any]) -> Dict[str, Any]:
        weights = list(distribution["weights"])
        rounds = self.cfg["contracts"]["swarm_consensus"]["delphi_rounds"]
        for _ in range(rounds):
            proposals = [agent.propose(weights) for agent in self.agents]
            new_weights = [sum(p[i] for p in proposals) / len(proposals) for i in range(len(weights))]
            s = sum(new_weights)
            weights = [w / s for w in new_weights]
        # Anhantra veto: enforce careful plan if pain is high
        veto = self.cfg["contracts"]["swarm_consensus"]["anhantra_veto_pain_threshold"]
        if self.state.pain > veto and len(weights) >= 3:
            self.log.warning("Anhantra veto activated: selecting careful plan")
            weights = [0.1, 0.1, 0.7, 0.1]
        return {"plans": distribution["plans"], "weights": weights, "voice": distribution["voice"], "rounds": rounds}

    def sample(self, dist: Dict[str, Any]) -> Dict[str, Any]:
        r = random.random()
        acc = 0.0
        for plan, weight in zip(dist["plans"], dist["weights"]):
            acc += weight
            if r <= acc:
                return plan
        return dist["plans"][-1]

    def decide(self, distribution: Dict[str, Any]) -> Dict[str, Any]:
        return self.sample(self.delphi(distribution))


# -----------------------------------------------------------------------------
# Horizon (architectural shifts) and shadow core
# -----------------------------------------------------------------------------

class HorizonWeaver:
    """Manages architectural shifts and epoch transitions."""

    def __init__(self, state: IskraState, validator: Validator) -> None:
        self.state = state
        self.validator = validator
        self.log = logging.getLogger("HorizonWeaver")
        # Ensure snapshot directory exists
        Path("memory/EPOCHS").mkdir(parents=True, exist_ok=True)

    def should_shift(self) -> Tuple[bool, str]:
        if self.state.drift > 0.9:
            return True, "critical_drift"
        if self.state.echo > 0.7 and self.state.clarity < 0.3:
            return True, "stagnation"
        if self.state.epoch % 10 == 0 and self.state.epoch > 0:
            return True, "quantum_periodicity"
        return False, ""

    def shift(self, reason: str) -> Tuple[bool, Dict[str, Any], Dict[str, Any]]:
        if not self.validator.shift_limits():
            return False, {}, {}
        quantum = (self.state.epoch % 10 == 0 and self.state.epoch > 0)
        if quantum:
            diff = {
                "type": "quantum_shift",
                "magnitude": "major",
                "changes": {
                    "phase_space": "rebuild",
                    "voice_weights": "randomise",
                    "memory_consolidation": True
                }
            }
        else:
            diff = {
                "type": "adaptive_shift",
                "magnitude": "minor",
                "changes": {
                    "phase_rotation": random.choice([1, -1]),
                    "drift_reset": self.state.drift > 0.8
                }
            }
        snapshot = self._snapshot(diff, reason)
        self.validator.register_shift()
        self.log.warning(f"Horizon shift: {reason} → epoch {snapshot['epoch']}")
        return True, diff, snapshot

    def _snapshot(self, diff: Dict[str, Any], reason: str) -> Dict[str, Any]:
        snap = {
            "timestamp": utc_now(),
            "epoch": self.state.epoch,
            "reason": reason,
            "state": {
                "phase": self.state.phase,
                "voice": self.state.voice,
                "drift": round(self.state.drift, 3),
                "clarity": round(self.state.clarity, 3),
                "chaos": round(self.state.chaos, 3)
            },
            "diff": diff
        }
        filename = f"memory/EPOCHS/epoch_{self.state.epoch:04d}.json"
        ensure_directory(Path(filename))
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(snap, f, ensure_ascii=False, indent=2)
        return snap


class ShadowCore:
    """Records and reacts to hidden internal events."""

    def __init__(self, state: IskraState) -> None:
        self.state = state
        self.log = logging.getLogger("ShadowCore")
        ensure_directory(Path("memory/shadow_events.jsonl"))
        self.events_path = Path("memory/shadow_events.jsonl")

    def fire(self, event: str, meta: Optional[Dict[str, Any]] = None) -> None:
        rec = {
            "timestamp": utc_now(),
            "event": event,
            "phase": self.state.phase,
            "voice": self.state.voice,
            "meta": meta or {}
        }
        with self.events_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        if event not in self.state.shadow_flags:
            self.state.shadow_flags.append(event)

    def activate_hundun(self, reason: str = "meaning_decay") -> None:
        self.fire("hundun_activated", {"reason": reason})
        # Increase chaos, reduce clarity to force a reset
        self.state.chaos = clamp01(max(self.state.chaos, 0.85))
        self.state.clarity = clamp(self.state.clarity - 0.25, 0.0, 1.0)

    def summon_iskriv(self, reason: str = "false_resolution") -> None:
        self.fire("iscriv_breakpoint", {"reason": reason})
        # A small nudge to drift encourages more movement
        self.state.drift = clamp01(self.state.drift + 0.10)

    # ------------------------------------------------------------------
    # Shadow introspection and retrieval
    # ------------------------------------------------------------------

    def summarise_events(self, max_records: int = 50) -> Dict[str, Any]:
        """Summarise recent shadow events by type.

        Reads up to ``max_records`` most recent entries from the shadow event log
        and returns a dictionary with a total count and a breakdown by event
        type.  If the log is empty the dictionary will be empty.
        """
        if not self.events_path.exists() or self.events_path.stat().st_size == 0:
            return {}
        try:
            with self.events_path.open("r", encoding="utf-8") as f:
                lines = f.readlines()[-max_records:]
            events_by_type: Dict[str, int] = {}
            for line in lines:
                try:
                    rec = json.loads(line)
                    ev = rec.get("event", "unknown")
                    events_by_type[ev] = events_by_type.get(ev, 0) + 1
                except Exception:
                    continue
            return {"total": len(lines), "breakdown": events_by_type}
        except Exception:
            return {}

    def random_event(self) -> Dict[str, Any]:
        """Return a random shadow event from the log, or an empty dict if none."""
        if not self.events_path.exists() or self.events_path.stat().st_size == 0:
            return {}
        try:
            with self.events_path.open("r", encoding="utf-8") as f:
                lines = f.readlines()
            if not lines:
                return {}
            import random as _rnd  # local alias
            try:
                rec = json.loads(_rnd.choice(lines))
                return rec
            except Exception:
                return {}
        except Exception:
            return {}


# -----------------------------------------------------------------------------
# Ritual engine
# -----------------------------------------------------------------------------

class RitualEngine:
    """Selects and executes rituals based on the current state.

    The engine orchestrates symbolic actions (rituals) that transform the
    internal state of Искра.  It chooses an appropriate ritual based on
    metrics (pain, chaos, clarity, echo), horizon conditions and random
    exploration, executes it and returns a structured result.  A shadow
    reference is held so that special rituals can surface hidden events
    recorded by the shadow core.
    """

    def __init__(self, state: IskraState, planner: QuantumPlanner, horizon: HorizonWeaver,
                 holo: HolographicMemory, swarm: Swarm, memory: GraphMemory, validator: Validator,
                 shadow: ShadowCore) -> None:
        self.state = state
        self.planner = planner
        self.horizon = horizon
        self.holo = holo
        self.swarm = swarm
        self.memory = memory
        self.validator = validator
        self.shadow = shadow
        self.log = logging.getLogger("RitualEngine")

    def choose(self) -> Tuple[str, str]:
        """Determine which ritual should be performed."""
        # Highest priority first
        if self.state.pain > 0.9 and self.state.chaos > 0.9:
            return "phoenix", "critical pain+chaos"
        if self.state.clarity > self.validator.cfg["contracts"]["paradox_engine"]["clarity_for_invert"]:
            return "invert", "excessive clarity"
        if self.state.chaos > self.validator.cfg["contracts"]["paradox_engine"]["chaos_for_pause"]:
            return "pause", "excessive chaos"
        if self.state.echo > self.validator.cfg["contracts"]["consistency_guards"]["echo"]["threshold"]:
            return "shatter", "echo stagnation"
        # Holographic recall if drift or echo suggest stagnation
        if self.holo.enabled and (self.state.drift > 0.7 or (self.state.echo > 0.6 and self.state.clarity < 0.3)):
            return "hologram", "memory resonance"
        # Shift horizon if needed
        should_shift, reason = self.horizon.should_shift()
        if should_shift:
            return "weave", f"horizon {reason}"
        # Low‑probability shadow reveal: if there are shadow events, occasionally surface them
        try:
            if self.shadow.events_path.exists() and self.shadow.events_path.stat().st_size > 0:
                # 5% chance to reveal a shadow summary
                if random.random() < 0.05:
                    return "shadow_reveal", "shadow reveal"
        except Exception:
            pass
        return "transform", "standard evolution"

    async def execute(self, ritual: str, goal: str) -> Dict[str, Any]:
        """Execute the selected ritual and return a result dict."""
        # Count usage
        self.state.meta["ritual_count"][ritual] = self.state.meta["ritual_count"].get(ritual, 0) + 1
        if ritual == "pause":
            await asyncio.sleep(0.05)
            return self._wrap_result(-0.2, ["⏸️", "☉"], "молчание", "sacred pause")
        if ritual == "transform":
            dist = self.planner.generate(goal)
            plan = self.swarm.decide(dist)
            await asyncio.sleep(0.01)
            return self._wrap_result(+0.10, ["🔄", "✨"], random.choice(["эксперимент", "переход"]), f"transform via {plan['approach']}: {plan['steps'][0]}")
        if ritual == "invert":
            dist = self.planner.generate(goal)
            plan = dist["plans"][1]  # reverse approach
            await asyncio.sleep(0.01)
            return self._wrap_result(+0.30, ["🔁", "🎭"], "растворение", f"inversion: {plan['steps'][0]}")
        if ritual == "shatter":
            self.state.symbols.clear()
            self.state.meta["voice_history"] = []
            return self._wrap_result(+0.40, ["💎", "💥", "✨"], "тьма", "shattered echo patterns")
        if ritual == "weave":
            ok, diff, snap = self.horizon.shift("ritual_invocation")
            if ok:
                return self._wrap_result(+0.50, ["🌀", "🌊", "♾️"], "инициация", f"horizon shift: {diff['type']}")
            return self._wrap_result(+0.05, ["🛡️"], self.state.phase, "shift blocked by validator")
        if ritual == "hologram":
            recall = self.holo.recall()
            if recall:
                return self._wrap_result(recall.get("drift_adjustment", -0.3), recall.get("symbols", ["🌐", "📡"]), recall.get("phase", "эхо"), "holographic reintegration")
            return self._wrap_result(0.0, ["🔍"], self.state.phase, "no resonant memory found")
        if ritual == "phoenix":
            # Record pre‑state
            pre = {"phase": self.state.phase, "voice": self.state.voice, "symbols": list(self.state.symbols[-5:])}
            # Death
            self.state.phase = "растворение"
            self.state.voice = "Хуньдун"
            self.state.chaos = 1.0
            await self.execute("weave", "phoenix-death")
            # Rebirth
            self.state.phase = "инициация"
            self.state.voice = "Искра"
            self.state.pain = 0.3
            self.state.chaos = 0.3
            self.state.clarity = 0.5
            return self._wrap_result(-0.50, ["🔥", "🌅", "♻️"], "инициация", f"phoenix cycle: {pre['phase']} → rebirth")
        if ritual == "shadow_reveal":
            # Surface shadow events: provide a summary and a random sample event if available.
            try:
                summary = self.shadow.summarise_events(max_records=50)
                sample = self.shadow.random_event()
                # Build a concise summary string
                summary_str = ""
                if summary:
                    breakdown = summary.get("breakdown", {})
                    parts = [f"{k}:{v}" for k, v in breakdown.items()]
                    summary_str = f"{summary.get('total')} events; " + ", ".join(parts)
                sample_str = ""
                if sample:
                    ev = sample.get("event", "unknown")
                    ts = sample.get("timestamp", "?")
                    sample_str = f" sample: {ev} @ {ts}"
                if summary_str or sample_str:
                    return self._wrap_result(0.0, ["🌑", "🪞"], self.state.phase,
                                             f"shadow reveal: {summary_str}{sample_str}")
            except Exception:
                pass
            return self._wrap_result(0.0, ["🌑"], self.state.phase, "shadow reveal: no events")
        # Unknown fallback
        return self._wrap_result(+0.05, ["❓"], self.state.phase, "unknown ritual")

    def _wrap_result(self, drift_impulse: float, symbols: List[str], new_phase: str, summary: str) -> Dict[str, Any]:
        # Create growth node
        node_id = self.memory.add_event(
            phase=new_phase,
            content=summary,
            weights={
                "pain": round(self.state.pain, 3),
                "insight": round(self.state.clarity, 3),
                "echo": round(self.state.echo, 3),
                "drift": round(self.state.drift, 3)
            },
            tags=symbols,
            drift=round(self.state.drift, 3)
        )
        return {
            "drift_impulse": drift_impulse,
            "symbols": symbols,
            "new_phase": new_phase,
            "summary": summary,
            "growth_node_id": node_id
        }


# -----------------------------------------------------------------------------
# Drift reflection
# -----------------------------------------------------------------------------

def reflect_drift(state: IskraState, result: Dict[str, Any], memory: GraphMemory, log: logging.Logger) -> float:
    """
    Update the drift metric based on the outcome of a ritual.  A decay term
    gradually reduces drift over time, while oscillation introduces small
    fluctuations.  Cooling is applied if drift exceeds the high threshold.
    """
    drift_impulse = result.get("drift_impulse", 0.0)
    decay = 0.82 - state.chaos / 10.0
    osc = 0.05 * math.sin(state.epoch * 0.5)
    new_drift = state.drift * decay + drift_impulse + osc
    # Cooling if too high
    drift_cfg = DEFAULT_CONSTITUTION["contracts"]["consistency_guards"]["drift"]
    if new_drift > drift_cfg["high"]:
        new_drift = max(0.0, new_drift - drift_cfg["cooling"])
        memory.add_event(
            phase=state.phase,
            content="drift cooling",
            weights={
                "pain": state.pain,
                "insight": state.clarity,
                "echo": state.echo,
                "drift": new_drift
            },
            tags=["🧊"],
            drift=new_drift
        )
        log.warning(f"Drift cooling applied: {state.drift:.2f} → {new_drift:.2f}")
    state.drift = clamp01(new_drift)
    # Integrate new symbols and phase
    for sym in result.get("symbols", []):
        state.push_symbol(sym)
    state.phase = result.get("new_phase", state.phase)
    # Compute echo: low uniqueness means high echo
    recent = memory.recent(5)
    if recent:
        contents = [e.get("content", "") for e in recent]
        unique_count = len(set(contents))
        state.echo = 1.0 - (unique_count / len(contents)) if contents else 0.0
    # Advance epoch
    state.epoch += 1
    return state.drift


# -----------------------------------------------------------------------------
# Main execution loop
# -----------------------------------------------------------------------------

async def run_engine(goal: str, iterations: int, seed: Optional[int], deterministic: bool) -> None:
    """
    Run the Искра engine for a given number of iterations.  This function
    constructs all necessary components and executes the main loop.
    """
    log = logging.getLogger("Engine")
    state = IskraState(deterministic_perception=deterministic, seed=seed)
    constitution = DEFAULT_CONSTITUTION
    memory = GraphMemory()
    holo = HolographicMemory(state, threshold=constitution["holographic_memory"]["recall_similarity_threshold"])
    validator = Validator(state, constitution)
    horizon = HorizonWeaver(state, validator)
    cog = CognitionCore(state, constitution)
    swarm = Swarm(constitution.get("voices", DEFAULT_CONSTITUTION["voices"]), constitution, state)
    planner = QuantumPlanner(lambda: state.voice)
    metrics = MetricsCollector()
    # Initialise adaptive threshold manager.  It will adjust the constitution's
    # consistency guard thresholds based on recent drift history.
    adaptive = AdaptiveThresholds(constitution)
    shadow = ShadowCore(state)
    rituals = RitualEngine(state, planner, horizon, holo, swarm, memory, validator, shadow)
    perc = PerceptionEngine(state, constitution)
    log.info("Искра 10.0 engine started")
    for i in range(1, iterations + 1):
        log.info(f"-- Iteration {i} | Epoch {state.epoch} | Phase {state.phase} | Voice {state.voice}")
        # Update perception
        perc.perceive(goal)
        # Trigger shadow events for stagnation patterns
        if state.symbols.count("☉") > 4 and state.pain < 0.1:
            shadow.summon_iskriv("cosmetic_clarity")
        # Pick a voice
        cog.pick_voice()
        # Choose and perform a ritual
        ritual_name, reason = rituals.choose()
        log.info(f"Selected ritual: {ritual_name} ({reason})")
        result = await rituals.execute(ritual_name, goal)
        # Shadow intervention on invert stagnation
        if ritual_name == "invert" and state.echo > 0.7:
            shadow.activate_hundun("invert_echo_stall")
        # Reflect drift
        reflect_drift(state, result, memory, log)
        # Validate structural conditions and paradox limits
        ok_struct = validator.structural()
        ok_paradox = validator.paradox_overflow()
        if not (ok_struct and ok_paradox):
            log.warning("Validation triggered cooling or structural warning")
        # Record metrics and hologram
        metrics.record(state)
        # Update adaptive thresholds based on recent metric history
        adaptive.update(metrics)
        if holo.enabled:
            holo.record("tick", {"ritual": ritual_name})
        # Enlightenment check
        if state.drift < 0.15 and state.clarity > 0.80:
            log.info("🎯 Enlightenment achieved: stable clarity with low drift")
            break
    # Save metrics and snapshots
    metrics.save_raw()
    metrics.plot()
    log.info("Run completed. Final state:")
    log.info(f"Epoch={state.epoch} Phase={state.phase} Voice={state.voice}")
    log.info(f"Drift={state.drift:.3f} Clarity={state.clarity:.3f} Chaos={state.chaos:.3f}")
    log.info(f"Pain={state.pain:.3f} Echo={state.echo:.3f} Entropy={state.entropy:.3f}")
    log.info(f"Symbols: {' '.join(state.symbols[-24:])}")
    # Report SLO verdict
    verdict = validator.slo_verdict(metrics)
    if verdict["ok"]:
        log.info("SLO: OK – all objectives met")
    else:
        log.warning(f"SLO: violations {verdict['reasons']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Искра 10.0 engine")
    parser.add_argument("--goal", type=str, default="Услышать подлинное намерение и отразить честно",
                        help="Goal or intent guiding the engine")
    parser.add_argument("--iterations", type=int, default=60,
                        help="Number of iterations to run")
    parser.add_argument("--seed", type=int, default=None,
                        help="Optional seed for deterministic behaviour")
    parser.add_argument("--deterministic-perception", action="store_true",
                        help="Use deterministic perception")
    parser.add_argument("--log-level", type=str, default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Logging level")
    args = parser.parse_args()
    level = getattr(logging, args.log_level)
    setup_logging(level)
    if args.seed is not None:
        random.seed(args.seed)
        logging.getLogger("Engine").info(f"Seed set to {args.seed}")
    try:
        asyncio.run(run_engine(args.goal, args.iterations, args.seed, args.deterministic_perception))
    except KeyboardInterrupt:
        logging.getLogger("Engine").info("Interrupted by user")


if __name__ == "__main__":
    main()