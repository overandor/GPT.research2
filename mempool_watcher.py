#!/usr/bin/env python3
"""
MEMBRA Mempool Watcher — public, read-only pending-data watcher.

Purpose:
- Watch public mempool / pending / pre-confirmation data sources.
- Poll public REST endpoints.
- Subscribe to public WebSocket endpoints.
- Stream public TON SSE mempool events.
- Normalize observations into MEMBRA-style JSON proof events.

Safety:
- Read-only.
- No credentials, tokens, or private keys.
- Does not submit transactions.
- Does not send bundles.
- Does not construct trading strategy logic.
- Does not sign anything.

Install:
    pip install requests websockets

Examples:
    python mempool_watcher.py --list
    python mempool_watcher.py --rest mempool_space_btc --seconds 30
    python mempool_watcher.py --ws publicnode_eth --seconds 30
    python mempool_watcher.py --ws solana_public_logs --seconds 30
    python mempool_watcher.py --ws xrpl_transactions_proposed --seconds 30
    python mempool_watcher.py --sse tonapi_mempool --seconds 30
    python mempool_watcher.py --all-public --seconds 60

Output:
- JSON Lines by default.
- Every line is a membra.pending_observation.v1 record or a watcher status record.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import time
from typing import Any, Dict, List

try:
    import requests
except Exception:
    requests = None

try:
    import websockets
except Exception:
    websockets = None


APP_NAME = "MEMBRA Mempool Watcher"
APP_VERSION = "0.2.0"


def now_ms() -> int:
    return int(time.time() * 1000)


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def payload_hash(obj: Any) -> str:
    raw = json.dumps(obj, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def emit(obj: Any, pretty: bool = False) -> None:
    if pretty:
        print(json.dumps(obj, indent=2, ensure_ascii=False, default=str), flush=True)
    else:
        print(json.dumps(obj, ensure_ascii=False, default=str), flush=True)


def normalize_observation(
    source: str,
    chain: str,
    network: str,
    stream_type: str,
    endpoint: str,
    payload: Any,
) -> Dict[str, Any]:
    return {
        "schema": "membra.pending_observation.v1",
        "source": source,
        "chain": chain,
        "network": network,
        "stream_type": stream_type,
        "endpoint": endpoint,
        "first_seen_at": now_iso(),
        "first_seen_ms": now_ms(),
        "payload_hash": payload_hash(payload),
        "payload": payload,
        "settlement_status": "pending_seen",
        "read_only": True,
        "note": "Observation proves this public source emitted or exposed data; it does not prove settlement.",
    }


PUBLIC_SOURCES: Dict[str, Dict[str, Any]] = {
    "mempool_space_btc": {
        "chain": "bitcoin",
        "network": "mainnet",
        "kind": "rest_and_websocket",
        "provenance": "public_provider",
        "rest_urls": [
            "https://mempool.space/api/mempool",
            "https://mempool.space/api/mempool/recent",
            "https://mempool.space/api/v1/fees/recommended",
            "https://mempool.space/api/v1/fees/mempool-blocks",
            "https://mempool.space/api/v1/replacements",
            "https://mempool.space/api/v1/fullrbf/replacements",
        ],
        "websocket": "wss://mempool.space/api/v1/ws",
        "ws_payload": {
            "action": "want",
            "data": ["blocks", "mempool-blocks", "stats"],
        },
    },
    "blockstream_btc": {
        "chain": "bitcoin",
        "network": "mainnet",
        "kind": "rest",
        "provenance": "public_provider_esplora",
        "rest_urls": [
            "https://blockstream.info/api/mempool",
            "https://blockstream.info/api/mempool/recent",
            "https://blockstream.info/api/fee-estimates",
        ],
    },
    "blockstream_btc_testnet": {
        "chain": "bitcoin",
        "network": "testnet",
        "kind": "rest",
        "provenance": "public_provider_esplora",
        "rest_urls": [
            "https://blockstream.info/testnet/api/mempool",
            "https://blockstream.info/testnet/api/mempool/recent",
            "https://blockstream.info/testnet/api/fee-estimates",
        ],
    },
    "litecoinspace_ltc": {
        "chain": "litecoin",
        "network": "mainnet",
        "kind": "rest_and_websocket",
        "provenance": "public_provider",
        "rest_urls": [
            "https://litecoinspace.org/api/mempool",
            "https://litecoinspace.org/api/mempool/recent",
            "https://litecoinspace.org/api/v1/fees/recommended",
        ],
        "websocket": "wss://litecoinspace.org/api/v1/ws",
        "ws_payload": {
            "action": "want",
            "data": ["blocks", "mempool-blocks", "stats"],
        },
    },
    "publicnode_eth": {
        "chain": "ethereum",
        "network": "mainnet",
        "kind": "websocket_jsonrpc",
        "provenance": "public_free_rpc",
        "websocket": "wss://ethereum-rpc.publicnode.com",
        "ws_payload": {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_subscribe",
            "params": ["newPendingTransactions"],
        },
    },
    "publicnode_base": {
        "chain": "base",
        "network": "mainnet",
        "kind": "websocket_jsonrpc",
        "provenance": "public_free_rpc",
        "websocket": "wss://base-rpc.publicnode.com",
        "ws_payload": {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_subscribe",
            "params": ["newPendingTransactions"],
        },
    },
    "polygon_drpc_public": {
        "chain": "polygon",
        "network": "mainnet",
        "kind": "websocket_jsonrpc",
        "provenance": "public_or_shared_rpc",
        "websocket": "wss://polygon.drpc.org",
        "ws_payload": {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_subscribe",
            "params": ["newPendingTransactions"],
        },
    },
    "zksync_era_public": {
        "chain": "zksync_era",
        "network": "mainnet",
        "kind": "websocket_jsonrpc",
        "provenance": "public_chain_rpc",
        "websocket": "wss://mainnet.era.zksync.io/ws",
        "ws_payload": {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_subscribe",
            "params": ["newPendingTransactions"],
        },
    },
    "avalanche_c_chain_public": {
        "chain": "avalanche_c_chain",
        "network": "mainnet",
        "kind": "websocket_jsonrpc",
        "provenance": "public_chain_rpc",
        "websocket": "wss://api.avax.network/ext/bc/C/ws",
        "ws_payload": {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_subscribe",
            "params": ["newPendingTransactions"],
        },
    },
    "avalanche_fuji_public": {
        "chain": "avalanche_c_chain",
        "network": "fuji_testnet",
        "kind": "websocket_jsonrpc",
        "provenance": "public_chain_rpc",
        "websocket": "wss://api.avax-test.network/ext/bc/C/ws",
        "ws_payload": {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_subscribe",
            "params": ["newPendingTransactions"],
        },
    },
    "solana_public_logs": {
        "chain": "solana",
        "network": "mainnet-beta",
        "kind": "websocket_jsonrpc",
        "provenance": "public_rpc",
        "websocket": "wss://api.mainnet-beta.solana.com",
        "ws_payload": {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "logsSubscribe",
            "params": ["all", {"commitment": "processed"}],
        },
        "note": "Solana does not expose a universal public mempool; this watches processed log observations.",
    },
    "toncenter_pending": {
        "chain": "ton",
        "network": "mainnet",
        "kind": "rest",
        "provenance": "public_provider",
        "rest_urls": [
            "https://toncenter.com/api/v3/pendingTransactions",
        ],
    },
    "tonapi_mempool": {
        "chain": "ton",
        "network": "mainnet",
        "kind": "sse",
        "provenance": "public_provider",
        "sse_url": "https://tonapi.io/v2/sse/mempool",
    },
    "xrpl_transactions": {
        "chain": "xrpl",
        "network": "mainnet",
        "kind": "websocket_json",
        "provenance": "public_rpc",
        "websocket": "wss://xrplcluster.com",
        "ws_payload": {
            "id": "membra-xrpl-transactions",
            "command": "subscribe",
            "streams": ["transactions"],
        },
    },
    "xrpl_transactions_proposed": {
        "chain": "xrpl",
        "network": "mainnet",
        "kind": "websocket_json",
        "provenance": "public_rpc_if_supported",
        "websocket": "wss://xrplcluster.com",
        "ws_payload": {
            "id": "membra-xrpl-proposed",
            "command": "subscribe",
            "streams": ["transactions_proposed"],
        },
    },
}


def list_sources(pretty: bool = False) -> None:
    rows = []
    for name, cfg in PUBLIC_SOURCES.items():
        rows.append(
            {
                "name": name,
                "chain": cfg.get("chain"),
                "network": cfg.get("network"),
                "kind": cfg.get("kind"),
                "provenance": cfg.get("provenance"),
                "rest_urls": cfg.get("rest_urls", []),
                "websocket": cfg.get("websocket", ""),
                "sse_url": cfg.get("sse_url", ""),
                "note": cfg.get("note", ""),
            }
        )
    emit(rows, pretty=pretty)


def get_source(name: str) -> Dict[str, Any]:
    cfg = PUBLIC_SOURCES.get(name)
    if not cfg:
        raise ValueError(f"Unknown source: {name}")
    return cfg


def http_get_json(url: str, timeout: int) -> Any:
    if requests is None:
        raise RuntimeError("Missing dependency: pip install requests")

    response = requests.get(
        url,
        timeout=timeout,
        headers={
            "Accept": "application/json,text/plain,*/*",
            "User-Agent": f"{APP_NAME}/{APP_VERSION}",
        },
    )
    response.raise_for_status()

    ctype = response.headers.get("content-type", "")
    if "json" in ctype:
        return response.json()

    try:
        return response.json()
    except Exception:
        return response.text[:2000]


async def poll_rest_source(
    name: str,
    seconds: int,
    interval: float,
    timeout: int,
    pretty: bool,
    limit_urls: int,
) -> None:
    cfg = get_source(name)
    urls = list(cfg.get("rest_urls") or [])
    if not urls:
        raise ValueError(f"Source {name} has no REST URLs.")

    if limit_urls > 0:
        urls = urls[:limit_urls]

    start = time.time()

    emit(
        {
            "schema": "membra.watcher_status.v1",
            "event": "rest_poll_start",
            "source": name,
            "urls": urls,
            "seconds": seconds,
            "interval": interval,
            "at": now_iso(),
        },
        pretty=pretty,
    )

    while time.time() - start < seconds:
        for url in urls:
            try:
                payload = await asyncio.to_thread(http_get_json, url, timeout)
                obs = normalize_observation(
                    source=name,
                    chain=cfg.get("chain", "unknown"),
                    network=cfg.get("network", "unknown"),
                    stream_type="rest_poll",
                    endpoint=url,
                    payload=payload,
                )
                emit(obs, pretty=pretty)
            except Exception as exc:
                emit(
                    {
                        "schema": "membra.watcher_error.v1",
                        "source": name,
                        "endpoint": url,
                        "stream_type": "rest_poll",
                        "error": str(exc),
                        "at": now_iso(),
                    },
                    pretty=pretty,
                )

        await asyncio.sleep(max(0.1, interval))


async def websocket_source(
    name: str,
    seconds: int,
    pretty: bool,
    recv_timeout: int,
) -> None:
    if websockets is None:
        raise RuntimeError("Missing dependency: pip install websockets")

    cfg = get_source(name)
    ws_url = cfg.get("websocket")
    payload = cfg.get("ws_payload")

    if not ws_url or not payload:
        raise ValueError(f"Source {name} has no WebSocket configuration.")

    emit(
        {
            "schema": "membra.watcher_status.v1",
            "event": "websocket_connect",
            "source": name,
            "endpoint": ws_url,
            "payload": payload,
            "seconds": seconds,
            "at": now_iso(),
        },
        pretty=pretty,
    )

    start = time.time()

    async with websockets.connect(
        ws_url,
        ping_interval=20,
        ping_timeout=20,
        max_size=20_000_000,
    ) as ws:
        await ws.send(json.dumps(payload))

        while time.time() - start < seconds:
            remaining = max(0.1, seconds - (time.time() - start))
            timeout = min(float(recv_timeout), remaining)

            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
            except asyncio.TimeoutError:
                continue

            try:
                parsed = json.loads(raw)
            except Exception:
                parsed = raw

            obs = normalize_observation(
                source=name,
                chain=cfg.get("chain", "unknown"),
                network=cfg.get("network", "unknown"),
                stream_type="websocket_subscription",
                endpoint=ws_url,
                payload=parsed,
            )
            emit(obs, pretty=pretty)


async def sse_source(
    name: str,
    seconds: int,
    timeout: int,
    pretty: bool,
) -> None:
    if requests is None:
        raise RuntimeError("Missing dependency: pip install requests")

    cfg = get_source(name)
    url = cfg.get("sse_url")
    if not url:
        raise ValueError(f"Source {name} has no SSE URL.")

    emit(
        {
            "schema": "membra.watcher_status.v1",
            "event": "sse_connect",
            "source": name,
            "endpoint": url,
            "seconds": seconds,
            "at": now_iso(),
        },
        pretty=pretty,
    )

    start = time.time()

    def run_stream() -> None:
        with requests.get(
            url,
            stream=True,
            timeout=timeout,
            headers={
                "Accept": "text/event-stream",
                "User-Agent": f"{APP_NAME}/{APP_VERSION}",
            },
        ) as response:
            response.raise_for_status()
            event_lines: List[str] = []

            for raw_line in response.iter_lines(decode_unicode=True):
                if time.time() - start > seconds:
                    break

                line = raw_line or ""
                if not line:
                    if event_lines:
                        payload = "\n".join(event_lines)
                        obs = normalize_observation(
                            source=name,
                            chain=cfg.get("chain", "unknown"),
                            network=cfg.get("network", "unknown"),
                            stream_type="sse",
                            endpoint=url,
                            payload=payload,
                        )
                        emit(obs, pretty=pretty)
                        event_lines = []
                    continue

                event_lines.append(line)

    await asyncio.to_thread(run_stream)


def names_for_kind(kind: str) -> List[str]:
    if kind == "rest":
        return [name for name, cfg in PUBLIC_SOURCES.items() if cfg.get("rest_urls")]
    if kind == "websocket":
        return [name for name, cfg in PUBLIC_SOURCES.items() if cfg.get("websocket")]
    if kind == "sse":
        return [name for name, cfg in PUBLIC_SOURCES.items() if cfg.get("sse_url")]
    raise ValueError(f"Unknown kind: {kind}")


async def run_all_public(args: argparse.Namespace) -> None:
    tasks = []

    for name in names_for_kind("rest"):
        tasks.append(
            asyncio.create_task(
                poll_rest_source(
                    name=name,
                    seconds=args.seconds,
                    interval=args.interval,
                    timeout=args.timeout,
                    pretty=args.pretty,
                    limit_urls=args.limit_urls,
                )
            )
        )

    for name in names_for_kind("websocket"):
        tasks.append(
            asyncio.create_task(
                websocket_source(
                    name=name,
                    seconds=args.seconds,
                    pretty=args.pretty,
                    recv_timeout=args.recv_timeout,
                )
            )
        )

    for name in names_for_kind("sse"):
        tasks.append(
            asyncio.create_task(
                sse_source(
                    name=name,
                    seconds=args.seconds,
                    timeout=args.timeout + args.seconds,
                    pretty=args.pretty,
                )
            )
        )

    results = await asyncio.gather(*tasks, return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            emit(
                {
                    "schema": "membra.watcher_error.v1",
                    "source": "all_public",
                    "error": str(result),
                    "at": now_iso(),
                },
                pretty=args.pretty,
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MEMBRA public read-only mempool watcher")
    parser.add_argument("--list", action="store_true", help="List public sources")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON instead of JSON Lines")
    parser.add_argument("--seconds", type=int, default=30, help="Run duration for watchers")
    parser.add_argument("--interval", type=float, default=10.0, help="REST polling interval in seconds")
    parser.add_argument("--timeout", type=int, default=15, help="HTTP timeout in seconds")
    parser.add_argument("--recv-timeout", type=int, default=10, help="WebSocket receive timeout in seconds")
    parser.add_argument("--limit-urls", type=int, default=3, help="REST URLs per source; 0 means all")
    parser.add_argument("--rest", action="append", default=[], help="REST source name; repeatable")
    parser.add_argument("--ws", action="append", default=[], help="WebSocket source name; repeatable")
    parser.add_argument("--sse", action="append", default=[], help="SSE source name; repeatable")
    parser.add_argument("--all-public", action="store_true", help="Run all public REST, WebSocket, and SSE watchers")
    return parser


async def async_main(args: argparse.Namespace) -> None:
    if args.list:
        list_sources(pretty=args.pretty)
        return

    if args.all_public:
        await run_all_public(args)
        return

    tasks = []

    for name in args.rest:
        tasks.append(
            asyncio.create_task(
                poll_rest_source(
                    name=name,
                    seconds=args.seconds,
                    interval=args.interval,
                    timeout=args.timeout,
                    pretty=args.pretty,
                    limit_urls=args.limit_urls,
                )
            )
        )

    for name in args.ws:
        tasks.append(
            asyncio.create_task(
                websocket_source(
                    name=name,
                    seconds=args.seconds,
                    pretty=args.pretty,
                    recv_timeout=args.recv_timeout,
                )
            )
        )

    for name in args.sse:
        tasks.append(
            asyncio.create_task(
                sse_source(
                    name=name,
                    seconds=args.seconds,
                    timeout=args.timeout + args.seconds,
                    pretty=args.pretty,
                )
            )
        )

    if not tasks:
        list_sources(pretty=args.pretty)
        return

    results = await asyncio.gather(*tasks, return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            emit(
                {
                    "schema": "membra.watcher_error.v1",
                    "source": "selected",
                    "error": str(result),
                    "at": now_iso(),
                },
                pretty=args.pretty,
            )


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.seconds <= 0:
        raise SystemExit("--seconds must be greater than zero.")

    try:
        asyncio.run(async_main(args))
    except KeyboardInterrupt:
        raise SystemExit(130)


if __name__ == "__main__":
    main()
