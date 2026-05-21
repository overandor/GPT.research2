#!/usr/bin/env python3
"""
multi_marketplace_publisher.py

Publishes cleaned research/IP/code assets to multiple sales endpoints.

Install:
  pip install requests stripe python-dotenv

Run:
  python scripts/multi_marketplace_publisher.py --assets ./SALE_READY_ASSETS --config marketplaces.example.json

Supported adapters:
  - stripe
  - lemonsqueezy
  - shopify
  - generic_post

Important:
  - This script creates listings/checkouts only.
  - Payment does not automatically transfer full IP ownership.
  - Full assignment or exclusivity should require a signed agreement.
"""

import argparse
import csv
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List

import requests

try:
    import stripe
except ImportError:  # pragma: no cover
    stripe = None


SECRET_PATTERNS = [
    r"sk_live_[A-Za-z0-9_]+",
    r"sk_test_[A-Za-z0-9_]+",
    r"pk_live_[A-Za-z0-9_]+",
    r"ghp_[A-Za-z0-9_]{20,}",
    r"github_pat_[A-Za-z0-9_]+",
    r"AKIA[0-9A-Z]{16}",
    r"AIza[0-9A-Za-z\-_]{35}",
    r"xox[baprs]-[A-Za-z0-9\-]+",
    r"(?i)api[_-]?key\s*=\s*['\"][^'\"]+['\"]",
    r"(?i)api[_-]?secret\s*=\s*['\"][^'\"]+['\"]",
    r"(?i)private[_-]?key\s*=\s*['\"][^'\"]+['\"]",
    r"(?i)client[_-]?secret\s*=\s*['\"][^'\"]+['\"]",
]


SKIP_SCAN_SUFFIXES = {
    ".zip", ".7z", ".tar", ".gz", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".pyc"
}


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    if path.is_file():
        files = [path]
        root = path.parent
    else:
        files = sorted(p for p in path.rglob("*") if p.is_file())
        root = path

    for file in files:
        h.update(str(file.relative_to(root)).encode("utf-8", errors="ignore"))
        h.update(b"\0")
        with file.open("rb") as f:
            for block in iter(lambda: f.read(1024 * 1024), b""):
                h.update(block)
    return h.hexdigest()


def path_size(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def scan_for_secrets(path: Path) -> List[str]:
    findings: List[str] = []
    files = [path] if path.is_file() else [p for p in path.rglob("*") if p.is_file()]

    for file in files:
        if file.suffix.lower() in SKIP_SCAN_SUFFIXES:
            continue
        try:
            text = file.read_text(encoding="utf-8", errors="ignore")[:2_000_000]
        except Exception:
            continue
        for pattern in SECRET_PATTERNS:
            if re.search(pattern, text):
                findings.append(f"{file}: matched {pattern[:48]}...")
                break
    return findings


def infer_price_usd(name: str) -> int:
    n = name.lower()
    if any(x in n for x in ["nih", "sbir", "grant", "biomed", "clinical"]):
        return 7500
    if any(x in n for x in ["jito", "solana", "drift", "flash", "trading", "alpha"]):
        return 5000
    if any(x in n for x in ["aegis", "crisis", "defense", "risk"]):
        return 7500
    if any(x in n for x in ["valuation", "proofbook", "diligence"]):
        return 2500
    return 1500


def build_asset_payload(asset: Path) -> Dict[str, Any]:
    name = asset.stem if asset.is_file() else asset.name
    clean = re.sub(r"[_\-]+", " ", name).strip().title()
    price = infer_price_usd(name)
    digest = sha256_path(asset)
    size = path_size(asset)
    return {
        "asset_name": name,
        "title": f"{clean} — Research-Grade Technical Archive",
        "description": (
            "Cleaned research/IP/code archive with provenance hash, documentation, and buyer-facing "
            "diligence material. Sold as technical research material. No financial advice, no profit "
            "guarantee, and no automatic full IP assignment."
        ),
        "price_usd": price,
        "price_cents": price * 100,
        "sha256": digest,
        "size_bytes": size,
        "path": str(asset),
        "metadata": {
            "sha256": digest,
            "asset_name": name,
            "sale_type": "research_archive_or_option_deposit",
            "requires_signed_assignment_for_full_ip_transfer": "true",
        },
    }


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


def publish_stripe(asset: Dict[str, Any], cfg: Dict[str, Any]) -> Dict[str, Any]:
    if stripe is None:
        raise RuntimeError("Missing package: pip install stripe")
    stripe.api_key = require_env(cfg["secret_env"])

    product = stripe.Product.create(
        name=asset["title"],
        description=asset["description"][:990],
        metadata=asset["metadata"],
    )
    price = stripe.Price.create(
        unit_amount=asset["price_cents"],
        currency=cfg.get("currency", "usd"),
        product=product.id,
    )
    link = stripe.PaymentLink.create(
        line_items=[{"price": price.id, "quantity": 1}],
        metadata=asset["metadata"],
        after_completion={
            "type": "hosted_confirmation",
            "hosted_confirmation": {
                "custom_message": (
                    "Payment received. Delivery and transfer terms are subject to manual review. "
                    "Full IP assignment requires a separate signed agreement."
                )
            },
        },
    )
    return {"marketplace": "stripe", "status": "created", "product_id": product.id, "price_id": price.id, "url": link.url}


def publish_lemonsqueezy(asset: Dict[str, Any], cfg: Dict[str, Any]) -> Dict[str, Any]:
    api_key = require_env(cfg["api_key_env"])
    store_id = require_env(cfg["store_id_env"])
    variant_id = require_env(cfg["variant_id_env"])
    payload = {
        "data": {
            "type": "checkouts",
            "attributes": {
                "custom_price": asset["price_cents"],
                "product_options": {
                    "name": asset["title"],
                    "description": asset["description"],
                    "receipt_thank_you_note": "Payment received. Full IP assignment requires a separate signed agreement.",
                    "enabled_variants": [int(variant_id)],
                },
                "checkout_data": {"custom": asset["metadata"]},
                "test_mode": cfg.get("test_mode", False),
            },
            "relationships": {
                "store": {"data": {"type": "stores", "id": str(store_id)}},
                "variant": {"data": {"type": "variants", "id": str(variant_id)}},
            },
        }
    }
    r = requests.post(
        "https://api.lemonsqueezy.com/v1/checkouts",
        headers={
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json",
            "Authorization": f"Bearer {api_key}",
        },
        json=payload,
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    return {"marketplace": "lemonsqueezy", "status": "created", "url": data["data"]["attributes"]["url"]}


def publish_shopify(asset: Dict[str, Any], cfg: Dict[str, Any]) -> Dict[str, Any]:
    token = require_env(cfg["token_env"])
    shop = cfg["shop"]
    api_version = cfg.get("api_version", "2025-01")
    url = f"https://{shop}/admin/api/{api_version}/products.json"
    payload = {
        "product": {
            "title": asset["title"],
            "body_html": f"<p>{asset['description']}</p><p>SHA-256: {asset['sha256']}</p>",
            "vendor": cfg.get("vendor", "Private Seller"),
            "product_type": cfg.get("product_type", "Digital Research Archive"),
            "status": cfg.get("status", "draft"),
            "tags": "research archive, code asset, IP option, due diligence",
            "variants": [{"price": str(asset["price_usd"]), "sku": asset["asset_name"], "inventory_management": None, "requires_shipping": False}],
            "metafields": [{"namespace": "provenance", "key": "sha256", "value": asset["sha256"], "type": "single_line_text_field"}],
        }
    }
    r = requests.post(url, headers={"X-Shopify-Access-Token": token, "Content-Type": "application/json"}, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()["product"]
    return {"marketplace": "shopify", "status": "created", "product_id": data["id"], "url": data.get("admin_graphql_api_id", "")}


def publish_generic_post(asset: Dict[str, Any], cfg: Dict[str, Any]) -> Dict[str, Any]:
    headers = cfg.get("headers", {}).copy()
    if cfg.get("token_env"):
        headers["Authorization"] = f"Bearer {require_env(cfg['token_env'])}"
    payload = {
        "title": asset["title"],
        "description": asset["description"],
        "price_usd": asset["price_usd"],
        "sha256": asset["sha256"],
        "size_bytes": asset["size_bytes"],
        "metadata": asset["metadata"],
    }
    r = requests.post(cfg["url"], headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    try:
        body = r.json()
    except Exception:
        body = {"text": r.text[:500]}
    return {"marketplace": cfg.get("name", "generic_post"), "status": "created", "url": body.get("url", ""), "response": body}


PUBLISHERS = {
    "stripe": publish_stripe,
    "lemonsqueezy": publish_lemonsqueezy,
    "shopify": publish_shopify,
    "generic_post": publish_generic_post,
}


def candidate_assets(assets_dir: Path) -> List[Path]:
    return [p for p in assets_dir.iterdir() if p.is_dir() or p.suffix.lower() in {".zip", ".tar", ".gz", ".7z"}]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets", required=True, help="Folder containing cleaned asset folders or archives")
    parser.add_argument("--config", required=True, help="Marketplace adapter JSON config")
    parser.add_argument("--out", default="./marketplace_publish_output")
    parser.add_argument("--allow-secret-findings", action="store_true")
    args = parser.parse_args()

    assets_dir = Path(args.assets).expanduser().resolve()
    out_dir = Path(args.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not assets_dir.exists():
        raise SystemExit(f"Assets folder does not exist: {assets_dir}")

    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    marketplaces = config.get("marketplaces", [])
    if not marketplaces:
        raise SystemExit("Config must include a non-empty marketplaces array")

    results: List[Dict[str, Any]] = []
    for asset_path in candidate_assets(assets_dir):
        print(f"\nAsset: {asset_path.name}")
        findings = scan_for_secrets(asset_path)
        if findings and not args.allow_secret_findings:
            print("SKIPPED: possible secrets found")
            for item in findings[:10]:
                print(f"  - {item}")
            continue

        asset = build_asset_payload(asset_path)
        for cfg in marketplaces:
            adapter = cfg["type"]
            try:
                result = PUBLISHERS[adapter](asset, cfg)
                print(f"  CREATED {adapter}: {result.get('url', '')}")
            except Exception as exc:
                result = {"marketplace": adapter, "status": "error", "error": str(exc), "url": ""}
                print(f"  ERROR {adapter}: {exc}")
            results.append({"asset_name": asset["asset_name"], "title": asset["title"], "price_usd": asset["price_usd"], "sha256": asset["sha256"], **result})

    json_path = out_dir / "publish_results.json"
    csv_path = out_dir / "publish_results.csv"
    json_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        fields = sorted(set().union(*(r.keys() for r in results))) if results else ["status"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    print("\nDone.")
    print(f"CSV: {csv_path}")
    print(f"JSON: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
