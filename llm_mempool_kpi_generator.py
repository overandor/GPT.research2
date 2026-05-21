#!/usr/bin/env python3
"""
MEMBRA LLM Mempool KPI Generator

Local-first KPI, novelty, and narrative generator for MEMBRA mempool watcher output.

Purpose:
- Consume JSONL emitted by mempool_watcher.py.
- Convert pending-data observations into measurable KPIs.
- Score novelty, proof density, chain coverage, stream diversity, and payload uniqueness.
- Generate an optional local LLM narrative using Ollama.

Safety:
- Read-only analytics.
- No API keys.
- No private keys.
- No transaction submission.
- No bundle submission.
- Does not construct trading strategy logic.
- Does not recommend front-running, sandwiching, liquidation, or exploit behavior.
- By default, the LLM receives only aggregate KPIs, not raw payloads.

Install:
    pip install requests

Ollama optional:
    ollama serve
    ollama pull llama3.1

Examples:
    python mempool_watcher.py --all-public --seconds 60 \
      | python llm_mempool_kpi_generator.py --stdin --markdown

    python mempool_watcher.py --ws publicnode_eth --seconds 30 \
      | python llm_mempool_kpi_generator.py --stdin --llm --ollama-model llama3.1

    python llm_mempool_kpi_generator.py --input mempool.jsonl --json

Output:
- Deterministic KPI report in JSON or Markdown.
- Optional Ollama narrative if --llm is enabled.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    import requests
except Exception:
    requests = None


APP_NAME = "MEMBRA LLM Mempool KPI Generator"
APP_VERSION = "0.1.0"

KNOWN_PUBLIC_CHAINS = {
    "bitcoin",
    "litecoin",
    "ethereum",
    "base",
    "polygon",
    "zksync_era",
    "avalanche_c_chain",
    "solana",
    "ton",
    "xrpl",
}

OBSERVATION_SCHEMA = "membra.pending_observation.v1"
ERROR_SCHEMA = "membra.watcher_error.v1"
STATUS_SCHEMA = "membra.watcher_status.v1"


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def normalized_entropy(counter: Counter) -> float:
    total = sum(counter.values())
    if total <= 0 or len(counter) <= 1:
        return 0.0

    entropy = 0.0
    for count in counter.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log(p, 2)

    max_entropy = math.log(len(counter), 2)
    if max_entropy <= 0:
        return 0.0

    return clamp(entropy / max_entropy)


def percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0

    values = sorted(values)
    if len(values) == 1:
        return values[0]

    rank = (len(values) - 1) * p
    lo = math.floor(rank)
    hi = math.ceil(rank)
    if lo == hi:
        return values[int(rank)]

    weight = rank - lo
    return values[lo] * (1.0 - weight) + values[hi] * weight


def iter_jsonl_from_stdin() -> Iterable[Dict[str, Any]]:
    for raw in sys.stdin:
        line = raw.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                yield obj
        except Exception:
            yield {
                "schema": ERROR_SCHEMA,
                "source": "stdin",
                "error": "invalid_jsonl_line",
                "line_preview": line[:200],
                "at": now_iso(),
            }


def iter_jsonl_from_file(path: str) -> Iterable[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    yield obj
            except Exception:
                yield {
                    "schema": ERROR_SCHEMA,
                    "source": path,
                    "error": "invalid_jsonl_line",
                    "line_preview": line[:200],
                    "at": now_iso(),
                }


def compact_payload_shape(payload: Any, max_keys: int = 50) -> Dict[str, Any]:
    """Return low-risk structural metadata about a payload without exposing full raw content."""
    if isinstance(payload, dict):
        keys = sorted(str(k) for k in payload.keys())[:max_keys]
        return {
            "type": "object",
            "key_count": len(payload),
            "keys_sample": keys,
        }

    if isinstance(payload, list):
        return {
            "type": "array",
            "length": len(payload),
            "first_item_type": type(payload[0]).__name__ if payload else "empty",
        }

    if isinstance(payload, str):
        return {
            "type": "string",
            "length": len(payload),
        }

    return {
        "type": type(payload).__name__,
    }


@dataclass
class KPIState:
    total_lines: int = 0
    observation_count: int = 0
    error_count: int = 0
    status_count: int = 0
    unknown_count: int = 0

    chains: Counter = field(default_factory=Counter)
    networks: Counter = field(default_factory=Counter)
    sources: Counter = field(default_factory=Counter)
    stream_types: Counter = field(default_factory=Counter)
    endpoints: Counter = field(default_factory=Counter)
    settlement_statuses: Counter = field(default_factory=Counter)

    payload_hashes: Counter = field(default_factory=Counter)
    payload_shapes: Counter = field(default_factory=Counter)
    source_chain_pairs: Counter = field(default_factory=Counter)

    first_seen_ms_values: List[float] = field(default_factory=list)
    observation_wall_times: List[float] = field(default_factory=list)
    samples: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)

    def add(self, obj: Dict[str, Any], sample_limit: int = 5) -> None:
        self.total_lines += 1
        schema = obj.get("schema", "")

        if schema == OBSERVATION_SCHEMA:
            self.observation_count += 1
            source = str(obj.get("source", "unknown"))
            chain = str(obj.get("chain", "unknown"))
            network = str(obj.get("network", "unknown"))
            stream_type = str(obj.get("stream_type", "unknown"))
            endpoint = str(obj.get("endpoint", "unknown"))
            settlement_status = str(obj.get("settlement_status", "pending_seen"))
            payload_hash = str(obj.get("payload_hash", ""))

            self.sources[source] += 1
            self.chains[chain] += 1
            self.networks[network] += 1
            self.stream_types[stream_type] += 1
            self.endpoints[endpoint] += 1
            self.settlement_statuses[settlement_status] += 1
            self.source_chain_pairs[f"{source}:{chain}"] += 1

            if payload_hash:
                self.payload_hashes[payload_hash] += 1

            payload = obj.get("payload")
            shape = compact_payload_shape(payload)
            self.payload_shapes[json.dumps(shape, sort_keys=True)] += 1

            first_seen_ms = safe_float(obj.get("first_seen_ms"), 0.0)
            if first_seen_ms > 0:
                self.first_seen_ms_values.append(first_seen_ms)

            self.observation_wall_times.append(time.time())

            if len(self.samples) < sample_limit:
                self.samples.append(
                    {
                        "source": source,
                        "chain": chain,
                        "network": network,
                        "stream_type": stream_type,
                        "endpoint": endpoint,
                        "payload_hash": payload_hash,
                        "payload_shape": shape,
                    }
                )

        elif schema == ERROR_SCHEMA:
            self.error_count += 1
            if len(self.errors) < sample_limit:
                self.errors.append(
                    {
                        "source": obj.get("source", "unknown"),
                        "endpoint": obj.get("endpoint", ""),
                        "error": obj.get("error", "unknown_error"),
                    }
                )

        elif schema == STATUS_SCHEMA:
            self.status_count += 1
        else:
            self.unknown_count += 1


def counter_top(counter: Counter, limit: int = 10) -> List[Dict[str, Any]]:
    return [{"name": key, "count": count} for key, count in counter.most_common(limit)]


def compute_report(state: KPIState, baseline_events_per_minute: float = 60.0) -> Dict[str, Any]:
    total_events = max(1, state.total_lines)
    observations = state.observation_count
    unique_hashes = len(state.payload_hashes)
    duplicate_hashes = sum(count - 1 for count in state.payload_hashes.values() if count > 1)

    if state.first_seen_ms_values:
        duration_ms = max(state.first_seen_ms_values) - min(state.first_seen_ms_values)
    else:
        duration_ms = 0.0

    duration_minutes = max(duration_ms / 60_000.0, 1.0 / 60.0)
    events_per_minute = observations / duration_minutes if observations else 0.0

    source_diversity = normalized_entropy(state.sources)
    chain_diversity = normalized_entropy(state.chains)
    stream_diversity = normalized_entropy(state.stream_types)
    endpoint_diversity = normalized_entropy(state.endpoints)

    chain_coverage = clamp(len(state.chains) / max(1, len(KNOWN_PUBLIC_CHAINS)))
    proof_density = clamp(observations / total_events)
    payload_uniqueness = clamp(unique_hashes / max(1, observations))
    error_penalty = clamp(state.error_count / total_events)
    burst_index = clamp(events_per_minute / max(1.0, baseline_events_per_minute))

    novelty_score = clamp(
        0.30 * payload_uniqueness
        + 0.20 * chain_coverage
        + 0.15 * source_diversity
        + 0.15 * stream_diversity
        + 0.10 * endpoint_diversity
        + 0.10 * burst_index
        - 0.20 * error_penalty
    )

    proof_utility_score = clamp(
        0.35 * proof_density
        + 0.25 * payload_uniqueness
        + 0.20 * chain_coverage
        + 0.10 * source_diversity
        + 0.10 * stream_diversity
        - 0.25 * error_penalty
    )

    liquidity_signal_score = clamp(
        0.35 * burst_index
        + 0.25 * stream_diversity
        + 0.20 * chain_coverage
        + 0.10 * source_diversity
        + 0.10 * payload_uniqueness
        - 0.20 * error_penalty
    )

    infrastructure_readiness_score = clamp(
        0.30 * proof_density
        + 0.20 * endpoint_diversity
        + 0.20 * stream_diversity
        + 0.15 * chain_coverage
        + 0.15 * source_diversity
        - 0.25 * error_penalty
    )

    composite_membra_score = clamp(
        0.30 * novelty_score
        + 0.25 * proof_utility_score
        + 0.20 * liquidity_signal_score
        + 0.25 * infrastructure_readiness_score
    )

    valuation_floor = round(1500 + 4500 * composite_membra_score)
    valuation_mid = round(3000 + 14000 * composite_membra_score)
    valuation_ceiling = round(7500 + 42500 * composite_membra_score)

    timestamps = state.first_seen_ms_values
    interarrival_ms: List[float] = []
    if len(timestamps) > 1:
        sorted_ts = sorted(timestamps)
        interarrival_ms = [b - a for a, b in zip(sorted_ts[:-1], sorted_ts[1:]) if b >= a]

    report = {
        "schema": "membra.llm_kpi_report.v1",
        "generated_at": now_iso(),
        "app": APP_NAME,
        "version": APP_VERSION,
        "summary": {
            "total_lines": state.total_lines,
            "observations": observations,
            "errors": state.error_count,
            "statuses": state.status_count,
            "unknown": state.unknown_count,
            "unique_payload_hashes": unique_hashes,
            "duplicate_payload_hashes": duplicate_hashes,
            "unique_sources": len(state.sources),
            "unique_chains": len(state.chains),
            "unique_stream_types": len(state.stream_types),
            "unique_endpoints": len(state.endpoints),
            "duration_ms": round(duration_ms, 2),
            "events_per_minute": round(events_per_minute, 4),
        },
        "kpis": {
            "payload_uniqueness": round(payload_uniqueness, 4),
            "chain_coverage": round(chain_coverage, 4),
            "source_diversity": round(source_diversity, 4),
            "chain_diversity": round(chain_diversity, 4),
            "stream_diversity": round(stream_diversity, 4),
            "endpoint_diversity": round(endpoint_diversity, 4),
            "proof_density": round(proof_density, 4),
            "burst_index": round(burst_index, 4),
            "error_penalty": round(error_penalty, 4),
            "novelty_score": round(novelty_score, 4),
            "proof_utility_score": round(proof_utility_score, 4),
            "liquidity_signal_score": round(liquidity_signal_score, 4),
            "infrastructure_readiness_score": round(infrastructure_readiness_score, 4),
            "composite_membra_score": round(composite_membra_score, 4),
        },
        "valuation_signal_usd": {
            "floor": valuation_floor,
            "mid": valuation_mid,
            "ceiling": valuation_ceiling,
            "method": "heuristic prototype valuation from novelty, proof utility, liquidity signal, and infrastructure readiness",
            "disclaimer": "Not a financial appraisal; use as an internal productization signal.",
        },
        "distributions": {
            "chains": counter_top(state.chains),
            "sources": counter_top(state.sources),
            "stream_types": counter_top(state.stream_types),
            "endpoints": counter_top(state.endpoints),
            "settlement_statuses": counter_top(state.settlement_statuses),
            "source_chain_pairs": counter_top(state.source_chain_pairs),
        },
        "timing": {
            "first_seen_ms_min": min(timestamps) if timestamps else None,
            "first_seen_ms_max": max(timestamps) if timestamps else None,
            "interarrival_ms_p50": round(percentile(interarrival_ms, 0.50), 2) if interarrival_ms else None,
            "interarrival_ms_p90": round(percentile(interarrival_ms, 0.90), 2) if interarrival_ms else None,
            "interarrival_ms_p99": round(percentile(interarrival_ms, 0.99), 2) if interarrival_ms else None,
        },
        "samples": state.samples,
        "errors_sample": state.errors,
        "interpretation": deterministic_interpretation(
            novelty_score=novelty_score,
            proof_utility_score=proof_utility_score,
            liquidity_signal_score=liquidity_signal_score,
            readiness_score=infrastructure_readiness_score,
            error_penalty=error_penalty,
        ),
    }

    return report


def tier(score: float) -> str:
    if score >= 0.80:
        return "institutional-grade signal"
    if score >= 0.60:
        return "strong prototype signal"
    if score >= 0.40:
        return "usable prototype signal"
    if score >= 0.20:
        return "early exploratory signal"
    return "weak signal"


def deterministic_interpretation(
    novelty_score: float,
    proof_utility_score: float,
    liquidity_signal_score: float,
    readiness_score: float,
    error_penalty: float,
) -> Dict[str, Any]:
    strengths = []
    risks = []
    next_steps = []

    if novelty_score >= 0.60:
        strengths.append("High payload novelty and/or broad source coverage.")
    else:
        next_steps.append("Increase observation diversity across chains, endpoints, and stream types.")

    if proof_utility_score >= 0.60:
        strengths.append("Proof layer is producing dense, hashable observation records.")
    else:
        next_steps.append("Persist JSONL output and add reproducible run manifests for stronger proof trails.")

    if liquidity_signal_score >= 0.60:
        strengths.append("Mempool velocity and stream diversity indicate useful pending-state activity.")
    else:
        next_steps.append("Run longer windows and compare against per-chain baselines for liquidity signal calibration.")

    if readiness_score >= 0.60:
        strengths.append("The watcher output is close to productizable infrastructure telemetry.")
    else:
        next_steps.append("Add storage, dashboards, CI smoke tests, and source health scoring.")

    if error_penalty >= 0.15:
        risks.append("Error rate is high enough to impair valuation confidence.")
    if not risks:
        risks.append("Primary risk is prototype status: no SLA, persistence layer, dashboard, or audited endpoint health yet.")

    return {
        "novelty_tier": tier(novelty_score),
        "proof_utility_tier": tier(proof_utility_score),
        "liquidity_signal_tier": tier(liquidity_signal_score),
        "infrastructure_readiness_tier": tier(readiness_score),
        "strengths": strengths,
        "risks": risks,
        "next_steps": next_steps,
    }


def build_llm_prompt(report: Dict[str, Any]) -> str:
    compact = {
        "summary": report.get("summary"),
        "kpis": report.get("kpis"),
        "valuation_signal_usd": report.get("valuation_signal_usd"),
        "top_chains": report.get("distributions", {}).get("chains", [])[:5],
        "top_sources": report.get("distributions", {}).get("sources", [])[:5],
        "top_stream_types": report.get("distributions", {}).get("stream_types", [])[:5],
        "errors_sample": report.get("errors_sample", [])[:3],
        "interpretation": report.get("interpretation"),
    }

    return (
        "You are MEMBRA ArchitectOS. Produce a concise research-grade KPI memo for a public, "
        "read-only mempool watcher. Do not provide trading instructions, exploit strategy, "
        "front-running guidance, sandwiching guidance, or transaction-submission advice. "
        "Focus on novelty, proof utility, infrastructure readiness, data quality, and productization.\n\n"
        "Required sections:\n"
        "1. THESIS\n"
        "2. KPI READOUT\n"
        "3. NOVELTY SCORE EXPLANATION\n"
        "4. PROOF LAYER\n"
        "5. PRODUCTIZATION NEXT STEPS\n"
        "6. RISK MODEL\n"
        "7. APPRAISAL SIGNAL\n\n"
        "KPI JSON:\n"
        f"{json.dumps(compact, indent=2, ensure_ascii=False)}"
    )


def call_ollama(prompt: str, model: str, url: str, timeout: int) -> Dict[str, Any]:
    if requests is None:
        return {
            "enabled": True,
            "ok": False,
            "error": "Missing dependency: pip install requests",
        }

    body = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
        },
    }

    try:
        response = requests.post(url, json=body, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        return {
            "enabled": True,
            "ok": True,
            "model": model,
            "url": url,
            "response": data.get("response", ""),
        }
    except Exception as exc:
        return {
            "enabled": True,
            "ok": False,
            "model": model,
            "url": url,
            "error": str(exc),
        }


def markdown_report(report: Dict[str, Any]) -> str:
    summary = report.get("summary", {})
    kpis = report.get("kpis", {})
    valuation = report.get("valuation_signal_usd", {})
    interpretation = report.get("interpretation", {})

    lines = []
    lines.append(f"# MEMBRA Mempool KPI Report")
    lines.append("")
    lines.append(f"Generated: `{report.get('generated_at')}`")
    lines.append("")
    lines.append("## 1. Thesis")
    lines.append(
        "The watcher output converts public pending-state observations into measurable proof objects. "
        "The KPI layer prices the run by novelty, proof density, source diversity, liquidity signal, and infrastructure readiness."
    )
    lines.append("")
    lines.append("## 2. KPI Readout")
    lines.append(f"- Observations: **{summary.get('observations', 0)}**")
    lines.append(f"- Errors: **{summary.get('errors', 0)}**")
    lines.append(f"- Unique chains: **{summary.get('unique_chains', 0)}**")
    lines.append(f"- Unique sources: **{summary.get('unique_sources', 0)}**")
    lines.append(f"- Unique stream types: **{summary.get('unique_stream_types', 0)}**")
    lines.append(f"- Unique payload hashes: **{summary.get('unique_payload_hashes', 0)}**")
    lines.append(f"- Events per minute: **{summary.get('events_per_minute', 0)}**")
    lines.append("")
    lines.append("## 3. Scores")
    for key in [
        "novelty_score",
        "proof_utility_score",
        "liquidity_signal_score",
        "infrastructure_readiness_score",
        "composite_membra_score",
    ]:
        lines.append(f"- {key}: **{kpis.get(key, 0)}**")
    lines.append("")
    lines.append("## 4. Valuation Signal")
    lines.append(f"- Floor: **${valuation.get('floor', 0):,}**")
    lines.append(f"- Mid: **${valuation.get('mid', 0):,}**")
    lines.append(f"- Ceiling: **${valuation.get('ceiling', 0):,}**")
    lines.append("")
    lines.append("## 5. Interpretation")
    lines.append(f"- Novelty tier: **{interpretation.get('novelty_tier', '')}**")
    lines.append(f"- Proof utility tier: **{interpretation.get('proof_utility_tier', '')}**")
    lines.append(f"- Liquidity signal tier: **{interpretation.get('liquidity_signal_tier', '')}**")
    lines.append(f"- Infrastructure readiness tier: **{interpretation.get('infrastructure_readiness_tier', '')}**")
    lines.append("")
    lines.append("## 6. Strengths")
    for item in interpretation.get("strengths", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## 7. Risks")
    for item in interpretation.get("risks", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## 8. Next Steps")
    for item in interpretation.get("next_steps", []):
        lines.append(f"- {item}")

    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MEMBRA local LLM mempool novelty KPI generator")
    parser.add_argument("--stdin", action="store_true", help="Read watcher JSONL from stdin")
    parser.add_argument("--input", default="", help="Read watcher JSONL from file")
    parser.add_argument("--json", action="store_true", help="Emit full JSON report")
    parser.add_argument("--markdown", action="store_true", help="Emit Markdown report")
    parser.add_argument("--llm", action="store_true", help="Generate local Ollama narrative from aggregate KPIs")
    parser.add_argument("--ollama-model", default="llama3.1", help="Ollama model name")
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434/api/generate", help="Ollama generate endpoint")
    parser.add_argument("--ollama-timeout", type=int, default=120, help="Ollama request timeout")
    parser.add_argument("--baseline-events-per-minute", type=float, default=60.0, help="Baseline used for burst scoring")
    parser.add_argument("--sample-limit", type=int, default=5, help="Number of low-risk samples to keep")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.stdin and not args.input:
        parser.error("Choose --stdin or --input FILE")

    state = KPIState()

    if args.stdin:
        iterator = iter_jsonl_from_stdin()
    else:
        iterator = iter_jsonl_from_file(args.input)

    for obj in iterator:
        state.add(obj, sample_limit=max(0, args.sample_limit))

    report = compute_report(state, baseline_events_per_minute=args.baseline_events_per_minute)

    if args.llm:
        prompt = build_llm_prompt(report)
        report["llm"] = call_ollama(
            prompt=prompt,
            model=args.ollama_model,
            url=args.ollama_url,
            timeout=args.ollama_timeout,
        )

    if args.markdown:
        print(markdown_report(report))
        if args.llm:
            llm = report.get("llm", {})
            print("\n## 9. Local LLM Narrative")
            if llm.get("ok"):
                print(llm.get("response", ""))
            else:
                print(f"LLM unavailable: {llm.get('error', 'unknown error')}")
        return

    # JSON is the default because it composes best with other infrastructure.
    print(json.dumps(report, indent=2 if args.json else None, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
