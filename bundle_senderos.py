#!/usr/bin/env python3
"""
MEMBRA Bundle SenderOS
Safe pre-signed bundle submission harness.

Supports:
- Jito Solana sendBundle / getBundleStatuses / getTipAccounts
- Flashbots Ethereum eth_sendBundle

Safety model:
- Dry-run by default.
- Requires --execute to actually submit.
- Accepts only pre-signed transactions.
- Does not create transactions.
- Does not hold trading strategy logic.
- Does not do sandwiching, front-running, liquidation logic, or arbitrage logic.
- For Flashbots, the auth key signs the relay request only, not the transactions.

Install minimal:
    pip install requests

Install Flashbots auth signing support:
    pip install requests eth-account eth-utils

Examples:

1. Jito dry-run:
    python bundle_senderos.py jito-send --tx-file solana_signed_txs.txt

2. Jito execute:
    python bundle_senderos.py jito-send --tx-file solana_signed_txs.txt --execute

3. Jito status:
    python bundle_senderos.py jito-status --bundle-id BUNDLE_ID

4. Jito tip accounts:
    python bundle_senderos.py jito-tip-accounts

5. Flashbots dry-run:
    python bundle_senderos.py flashbots-send \
      --tx-file evm_signed_txs.txt \
      --block-number 0x123456

6. Flashbots execute:
    FLASHBOTS_AUTH_PRIVATE_KEY=0xYOUR_AUTH_KEY python bundle_senderos.py flashbots-send \
      --tx-file evm_signed_txs.txt \
      --block-number 0x123456 \
      --execute

Input files:
- One signed transaction per line.
- Blank lines and # comments are ignored.

Solana/Jito:
- Transactions should be base64 or base58 encoded signed Solana transactions.
- This script does not add tips. Include your tip instruction in your signed tx bundle if required by your flow.

EVM/Flashbots:
- Transactions should be raw signed tx hex strings, usually starting with 0x.
- The Flashbots auth key should be a separate unfunded identity key.
"""

import argparse
import json
import os
import sys
import time
import hashlib
from typing import Any, Dict, List, Optional

try:
    import requests
except Exception as exc:
    raise SystemExit("Missing dependency. Install with: pip install requests") from exc


# ============================================================
# CONFIG
# ============================================================

APP_NAME = "MEMBRA Bundle SenderOS"
APP_VERSION = "0.1.0"

JITO_MAINNET_BUNDLE_URL = "https://mainnet.block-engine.jito.wtf:443/api/v1/bundles"

JITO_REGIONAL_BUNDLE_URLS = {
    "mainnet": "https://mainnet.block-engine.jito.wtf:443/api/v1/bundles",
    "amsterdam": "https://amsterdam.mainnet.block-engine.jito.wtf:443/api/v1/bundles",
    "frankfurt": "https://frankfurt.mainnet.block-engine.jito.wtf:443/api/v1/bundles",
    "ny": "https://ny.mainnet.block-engine.jito.wtf:443/api/v1/bundles",
    "tokyo": "https://tokyo.mainnet.block-engine.jito.wtf:443/api/v1/bundles",
}

FLASHBOTS_RELAYS = {
    "mainnet": "https://relay.flashbots.net",
    "sepolia": "https://relay-sepolia.flashbots.net",
}

DEFAULT_TIMEOUT = 30


# ============================================================
# UTILS
# ============================================================

def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def print_json(obj: Any) -> None:
    print(json.dumps(obj, indent=2, ensure_ascii=False, default=str))


def read_lines_file(path: str) -> List[str]:
    if not path:
        raise ValueError("Missing --tx-file")

    with open(path, "r", encoding="utf-8") as f:
        lines = []

        for raw in f.readlines():
            line = raw.strip()

            if not line:
                continue

            if line.startswith("#"):
                continue

            lines.append(line)

    return lines


def jsonrpc_body(method: str, params: Any, request_id: int = 1) -> Dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params,
    }


def post_json(
    url: str,
    body: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    headers = headers or {}
    headers.setdefault("Content-Type", "application/json")
    headers.setdefault("User-Agent", f"{APP_NAME}/{APP_VERSION}")

    response = requests.post(url, headers=headers, data=json.dumps(body), timeout=timeout)

    out = {
        "http_status": response.status_code,
        "url": url,
    }

    try:
        out["response"] = response.json()
    except Exception:
        out["response_text"] = response.text

    if response.status_code >= 400:
        out["error"] = f"HTTP {response.status_code}"

    return out


def dry_run_report(
    provider: str,
    endpoint: str,
    method: str,
    body: Dict[str, Any],
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    body_text = json.dumps(body, sort_keys=True, default=str)

    return {
        "dry_run": True,
        "provider": provider,
        "endpoint": endpoint,
        "method": method,
        "generated_at": now_iso(),
        "request_hash": sha256_text(body_text),
        "request_body": body,
        "extra": extra or {},
        "notice": "Dry-run only. Pass --execute to submit this request.",
    }


# ============================================================
# JITO SOLANA
# ============================================================

def resolve_jito_url(region: str, custom_url: str = "") -> str:
    if custom_url:
        return custom_url

    region = (region or "mainnet").strip().lower()

    if region not in JITO_REGIONAL_BUNDLE_URLS:
        raise ValueError(
            f"Unknown Jito region '{region}'. "
            f"Known: {', '.join(sorted(JITO_REGIONAL_BUNDLE_URLS))}"
        )

    return JITO_REGIONAL_BUNDLE_URLS[region]


def jito_headers(auth_token: str = "") -> Dict[str, str]:
    headers = {
        "Content-Type": "application/json",
    }

    # Some Jito access paths may use an auth token / UUID depending on account setup.
    # If not required by your endpoint, leave it blank.
    if auth_token:
        headers["x-jito-auth"] = auth_token

    return headers


def jito_tip_accounts(region: str, custom_url: str, auth_token: str, execute: bool) -> Dict[str, Any]:
    url = resolve_jito_url(region, custom_url)
    body = jsonrpc_body("getTipAccounts", [], 1)

    if not execute:
        return dry_run_report("jito", url, "getTipAccounts", body)

    return post_json(url, body, headers=jito_headers(auth_token))


def jito_send_bundle(
    txs: List[str],
    region: str,
    custom_url: str,
    auth_token: str,
    execute: bool,
    encoding: str = "",
) -> Dict[str, Any]:
    if not txs:
        raise ValueError("No signed transactions supplied.")

    if len(txs) > 5:
        raise ValueError("Jito bundles should contain at most 5 signed transactions.")

    url = resolve_jito_url(region, custom_url)

    # Jito JSON-RPC examples commonly use params as a single array of tx strings.
    # Some integrations may add an options object; keep this default simple and official-style.
    params: List[Any] = [txs]

    if encoding:
        params.append({"encoding": encoding})

    body = jsonrpc_body("sendBundle", params, 1)

    extra = {
        "tx_count": len(txs),
        "encoding": encoding or "provider_default",
        "warning": (
            "Transactions must already be signed. This script does not add compute budget, "
            "priority fee, or tip instructions."
        ),
    }

    if not execute:
        return dry_run_report("jito", url, "sendBundle", body, extra)

    return post_json(url, body, headers=jito_headers(auth_token))


def jito_get_bundle_statuses(
    bundle_ids: List[str],
    region: str,
    custom_url: str,
    auth_token: str,
    execute: bool,
) -> Dict[str, Any]:
    if not bundle_ids:
        raise ValueError("No bundle IDs supplied.")

    url = resolve_jito_url(region, custom_url)
    body = jsonrpc_body("getBundleStatuses", [bundle_ids], 1)

    if not execute:
        return dry_run_report("jito", url, "getBundleStatuses", body)

    return post_json(url, body, headers=jito_headers(auth_token))


# ============================================================
# FLASHBOTS ETHEREUM
# ============================================================

def flashbots_signing_headers(body: Dict[str, Any], auth_private_key: str) -> Dict[str, str]:
    """
    Creates X-Flashbots-Signature.

    Requires:
        pip install eth-account eth-utils

    The auth key is an identity key for relay authentication.
    It should not be a funded key.
    """
    try:
        from eth_account import Account
        from eth_account.messages import encode_defunct
        from eth_utils import keccak
    except Exception as exc:
        raise RuntimeError(
            "Flashbots signing requires: pip install eth-account eth-utils"
        ) from exc

    if not auth_private_key:
        raise ValueError(
            "Missing Flashbots auth key. Set FLASHBOTS_AUTH_PRIVATE_KEY or pass --auth-private-key."
        )

    body_text = json.dumps(body, separators=(",", ":"), ensure_ascii=False)
    body_hash_hex = keccak(text=body_text).hex()

    message = encode_defunct(hexstr=body_hash_hex)
    signed = Account.sign_message(message, private_key=auth_private_key)
    address = Account.from_key(auth_private_key).address

    return {
        "Content-Type": "application/json",
        "X-Flashbots-Signature": f"{address}:{signed.signature.hex()}",
    }


def normalize_hex_tx(tx: str) -> str:
    tx = tx.strip()

    if not tx:
        return tx

    if not tx.startswith("0x"):
        tx = "0x" + tx

    return tx


def flashbots_send_bundle(
    txs: List[str],
    network: str,
    block_number: str,
    relay_url: str,
    auth_private_key: str,
    execute: bool,
    min_timestamp: Optional[int] = None,
    max_timestamp: Optional[int] = None,
    reverting_tx_hashes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    if not txs:
        raise ValueError("No raw signed EVM transactions supplied.")

    if len(txs) > 100:
        raise ValueError("Flashbots bundles can contain at most 100 transactions.")

    txs = [normalize_hex_tx(tx) for tx in txs]

    if not block_number:
        raise ValueError("Missing --block-number. Use hex, e.g. 0x123456.")

    if not block_number.startswith("0x"):
        raise ValueError("--block-number must be hex, e.g. 0x123456.")

    if relay_url:
        url = relay_url
    else:
        network = (network or "mainnet").strip().lower()
        if network not in FLASHBOTS_RELAYS:
            raise ValueError(f"Unknown Flashbots network: {network}")
        url = FLASHBOTS_RELAYS[network]

    bundle_params: Dict[str, Any] = {
        "txs": txs,
        "blockNumber": block_number,
    }

    if min_timestamp is not None:
        bundle_params["minTimestamp"] = int(min_timestamp)

    if max_timestamp is not None:
        bundle_params["maxTimestamp"] = int(max_timestamp)

    if reverting_tx_hashes:
        bundle_params["revertingTxHashes"] = reverting_tx_hashes

    body = jsonrpc_body("eth_sendBundle", [bundle_params], 1)

    extra = {
        "tx_count": len(txs),
        "network": network,
        "relay": url,
        "block_number": block_number,
        "warning": (
            "Transactions must already be signed. This script does not construct, simulate, "
            "price, or optimize transactions."
        ),
    }

    if not execute:
        return dry_run_report("flashbots", url, "eth_sendBundle", body, extra)

    headers = flashbots_signing_headers(body, auth_private_key)
    return post_json(url, body, headers=headers)


# ============================================================
# CLI
# ============================================================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="MEMBRA Bundle SenderOS — safe pre-signed bundle submission harness"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # Jito tip accounts
    p_tip = sub.add_parser("jito-tip-accounts", help="Call Jito getTipAccounts")
    p_tip.add_argument("--region", default="mainnet", choices=sorted(JITO_REGIONAL_BUNDLE_URLS))
    p_tip.add_argument("--url", default="", help="Custom Jito bundle endpoint")
    p_tip.add_argument("--auth-token", default=os.getenv("JITO_AUTH_TOKEN", ""))
    p_tip.add_argument("--execute", action="store_true", help="Actually send request")

    # Jito send
    p_jito = sub.add_parser("jito-send", help="Send Jito Solana bundle of pre-signed txs")
    p_jito.add_argument("--tx-file", required=True, help="File with one signed Solana tx per line")
    p_jito.add_argument("--region", default="mainnet", choices=sorted(JITO_REGIONAL_BUNDLE_URLS))
    p_jito.add_argument("--url", default="", help="Custom Jito bundle endpoint")
    p_jito.add_argument("--auth-token", default=os.getenv("JITO_AUTH_TOKEN", ""))
    p_jito.add_argument("--encoding", default="", choices=["", "base64", "base58"], help="Optional Jito encoding option")
    p_jito.add_argument("--execute", action="store_true", help="Actually submit bundle")

    # Jito status
    p_status = sub.add_parser("jito-status", help="Call Jito getBundleStatuses")
    p_status.add_argument("--bundle-id", action="append", default=[], help="Bundle ID; repeatable")
    p_status.add_argument("--bundle-id-file", default="", help="File with one bundle ID per line")
    p_status.add_argument("--region", default="mainnet", choices=sorted(JITO_REGIONAL_BUNDLE_URLS))
    p_status.add_argument("--url", default="", help="Custom Jito bundle endpoint")
    p_status.add_argument("--auth-token", default=os.getenv("JITO_AUTH_TOKEN", ""))
    p_status.add_argument("--execute", action="store_true", help="Actually send request")

    # Flashbots send
    p_fb = sub.add_parser("flashbots-send", help="Send Flashbots Ethereum bundle of raw signed txs")
    p_fb.add_argument("--tx-file", required=True, help="File with one raw signed EVM tx per line")
    p_fb.add_argument("--network", default="mainnet", choices=sorted(FLASHBOTS_RELAYS))
    p_fb.add_argument("--relay-url", default="", help="Custom Flashbots relay URL")
    p_fb.add_argument("--block-number", required=True, help="Target block as hex, e.g. 0x123456")
    p_fb.add_argument("--auth-private-key", default=os.getenv("FLASHBOTS_AUTH_PRIVATE_KEY", ""))
    p_fb.add_argument("--min-timestamp", type=int, default=None)
    p_fb.add_argument("--max-timestamp", type=int, default=None)
    p_fb.add_argument("--reverting-tx-hash", action="append", default=[])
    p_fb.add_argument("--execute", action="store_true", help="Actually submit bundle")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "jito-tip-accounts":
            result = jito_tip_accounts(
                region=args.region,
                custom_url=args.url,
                auth_token=args.auth_token,
                execute=args.execute,
            )
            print_json(result)
            return

        if args.command == "jito-send":
            txs = read_lines_file(args.tx_file)
            result = jito_send_bundle(
                txs=txs,
                region=args.region,
                custom_url=args.url,
                auth_token=args.auth_token,
                execute=args.execute,
                encoding=args.encoding,
            )
            print_json(result)
            return

        if args.command == "jito-status":
            bundle_ids = list(args.bundle_id or [])

            if args.bundle_id_file:
                bundle_ids.extend(read_lines_file(args.bundle_id_file))

            result = jito_get_bundle_statuses(
                bundle_ids=bundle_ids,
                region=args.region,
                custom_url=args.url,
                auth_token=args.auth_token,
                execute=args.execute,
            )
            print_json(result)
            return

        if args.command == "flashbots-send":
            txs = read_lines_file(args.tx_file)
            result = flashbots_send_bundle(
                txs=txs,
                network=args.network,
                block_number=args.block_number,
                relay_url=args.relay_url,
                auth_private_key=args.auth_private_key,
                execute=args.execute,
                min_timestamp=args.min_timestamp,
                max_timestamp=args.max_timestamp,
                reverting_tx_hashes=args.reverting_tx_hash or [],
            )
            print_json(result)
            return

        parser.print_help()

    except KeyboardInterrupt:
        raise SystemExit(130)

    except Exception as exc:
        print_json({
            "error": str(exc),
            "command": args.command,
            "notice": "No bundle was submitted unless --execute reached the provider successfully.",
        })
        raise SystemExit(1)


if __name__ == "__main__":
    main()
