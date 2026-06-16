"""
DECEPTR - Canary Token Manager (P3)
Generates and tracks canary tokens embedded in fake documents.
When a token is triggered (file opened, URL clicked), an alert is raised.
"""

import os
import uuid
import hashlib
import logging
import json
from datetime import datetime
from pathlib import Path

import requests

logger = logging.getLogger("deceptr.canary")

# Simple file-based store (replace with MySQL/Redis in production)
STORE_PATH = Path(os.getenv("CANARY_STORE_PATH", "/tmp/deceptr_canary_store.json"))


def _load_store() -> dict:
    if STORE_PATH.exists():
        try:
            return json.loads(STORE_PATH.read_text())
        except Exception:
            pass
    return {}


def _save_store(data: dict):
    STORE_PATH.write_text(json.dumps(data, indent=2))


def generate_token(doc_name: str, token_type: str = "url") -> dict:
    """
    Generate a new canary token for a fake document.
    token_type: 'url' or 'dns'
    Returns: {token_id, token_url, doc_name, created_at}
    """
    store = _load_store()
    token_id = hashlib.sha256(uuid.uuid4().bytes).hexdigest()[:16]
    base_url = os.getenv("CANARY_WEBHOOK_URL", "http://127.0.0.1:8000/api/canary/trigger")
    dns_domain = os.getenv("CANARY_DNS_DOMAIN", "canary.deceptr.local")

    if token_type == "url":
        token_url = f"{base_url}?token_id={token_id}"
    else:
        token_url = f"http://{token_id}.{dns_domain}"

    record = {
        "token_id": token_id,
        "doc_name": doc_name,
        "token_type": token_type,
        "token_url": token_url,
        "created_at": datetime.utcnow().isoformat(),
        "triggers": [],
    }
    store[token_id] = record
    _save_store(store)

    logger.info(f"[CANARY] Token created: {token_id} for doc '{doc_name}'")
    return record


def handle_trigger(token_id: str, source_ip: str = "unknown") -> dict:
    """
    Called when a canary token is triggered.
    Logs the event and sends a webhook alert.
    """
    store = _load_store()
    if token_id not in store:
        logger.warning(f"[CANARY] Unknown token triggered: {token_id} from {source_ip}")
        return {"status": "unknown_token"}

    record = store[token_id]
    trigger_event = {
        "source_ip": source_ip,
        "triggered_at": datetime.utcnow().isoformat(),
    }
    record["triggers"].append(trigger_event)
    store[token_id] = record
    _save_store(store)

    doc_name = record["doc_name"]
    logger.critical(
        f"[CANARY] *** TOKEN TRIGGERED *** token={token_id} doc='{doc_name}' ip={source_ip}"
    )

    _send_alert(token_id, doc_name, source_ip)

    return {
        "status": "triggered",
        "token_id": token_id,
        "doc_name": doc_name,
        "source_ip": source_ip,
    }


def _send_alert(token_id: str, doc_name: str, source_ip: str):
    """Send alert to configured webhook (Slack, Teams, etc.)"""
    webhook_url = os.getenv("ELASTALERT_SLACK_WEBHOOK", "")
    if not webhook_url:
        logger.warning("[CANARY] No webhook URL configured, alert not sent")
        return

    message = {
        "text": (
            f":warning: *CANARY TOKEN TRIGGERED* :warning:\n"
            f"• Token ID: `{token_id}`\n"
            f"• Document: `{doc_name}`\n"
            f"• Source IP: `{source_ip}`\n"
            f"• Time: `{datetime.utcnow().isoformat()} UTC`\n"
            f"• Action: Investigate immediately!"
        )
    }
    try:
        resp = requests.post(webhook_url, json=message, timeout=5)
        resp.raise_for_status()
        logger.info(f"[CANARY] Alert sent to webhook for token {token_id}")
    except Exception as e:
        logger.error(f"[CANARY] Failed to send webhook: {e}")


def list_tokens() -> list:
    """List all canary tokens and their trigger history."""
    store = _load_store()
    return list(store.values())
