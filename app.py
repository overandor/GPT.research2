#!/usr/bin/env python3
"""
MEMBRA Production API

FastAPI service for the public, read-only mempool watcher and KPI generator.

Safety:
- No API keys required.
- No private keys accepted.
- No transaction construction.
- No transaction submission.
- No bundle submission.
- KPI generation accepts observation JSON only.
"""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from llm_mempool_kpi_generator import KPIState, compute_report, markdown_report
from mempool_watcher import APP_VERSION as WATCHER_VERSION
from mempool_watcher import PUBLIC_SOURCES


APP_VERSION = "0.1.0"

app = FastAPI(
    title="MEMBRA Mempool Intelligence API",
    description=(
        "Public, read-only mempool observation metadata and KPI generation service. "
        "This API does not accept private keys, submit transactions, or send bundles."
    ),
    version=APP_VERSION,
)


class ObservationBatch(BaseModel):
    observations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="JSON objects emitted by mempool_watcher.py, usually JSONL-decoded records.",
    )
    baseline_events_per_minute: float = Field(default=60.0, ge=1.0)
    markdown: bool = Field(default=False)


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "ok": True,
        "service": "membra-mempool-intelligence-api",
        "version": APP_VERSION,
        "watcher_version": WATCHER_VERSION,
        "read_only": True,
    }


@app.get("/sources")
def sources() -> Dict[str, Any]:
    return {
        "count": len(PUBLIC_SOURCES),
        "sources": [
            {
                "name": name,
                "chain": cfg.get("chain"),
                "network": cfg.get("network"),
                "kind": cfg.get("kind"),
                "provenance": cfg.get("provenance"),
                "has_rest": bool(cfg.get("rest_urls")),
                "has_websocket": bool(cfg.get("websocket")),
                "has_sse": bool(cfg.get("sse_url")),
                "note": cfg.get("note", ""),
            }
            for name, cfg in sorted(PUBLIC_SOURCES.items())
        ],
    }


@app.post("/kpi/report")
def kpi_report(batch: ObservationBatch) -> Dict[str, Any]:
    if not batch.observations:
        raise HTTPException(status_code=400, detail="observations must not be empty")

    state = KPIState()
    for obj in batch.observations:
        state.add(obj)

    report = compute_report(
        state,
        baseline_events_per_minute=batch.baseline_events_per_minute,
    )

    if batch.markdown:
        return {
            "schema": "membra.api_markdown_report.v1",
            "markdown": markdown_report(report),
            "report": report,
        }

    return report


@app.get("/")
def root() -> Dict[str, Any]:
    return {
        "name": "MEMBRA Mempool Intelligence API",
        "version": APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "sources": "/sources",
        "kpi_report": "/kpi/report",
        "safety": {
            "read_only": True,
            "accepts_private_keys": False,
            "submits_transactions": False,
            "sends_bundles": False,
        },
    }
