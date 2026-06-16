"""
DECEPTR - Active Responder Module (P3)
Blocks attacker IPs via firewall API on CRITICAL alerts.
Disabled by default (MockBlocker). Set FIREWALL_ENABLED=true to activate.

Interface: FirewallBlocker (abstract)
Implementations: PfSenseBlocker, MockBlocker (for testing/demo)
"""

import os
import logging
import asyncio
import platform
from abc import ABC, abstractmethod
from datetime import datetime

logger = logging.getLogger("deceptr.responder")

# ── Allowlist: never block these IPs ─────────────────────────────────────────
ALLOWLIST = {
    "127.0.0.1",
    "8.8.8.8",
    "10.0.0.1",
}

BLOCK_SEVERITIES = {"CRITICAL", "HIGH"}
BLOCK_MIN_ABUSE_SCORE = 80


# ── Abstract Interface ────────────────────────────────────────────────────────
class FirewallBlocker(ABC):
    @abstractmethod
    def block_ip(self, ip: str, reason: str) -> dict:
        """Block an IP. Returns dict with status and details."""

    @abstractmethod
    def unblock_ip(self, ip: str) -> dict:
        """Unblock an IP."""

    @abstractmethod
    def list_blocked(self) -> list:
        """List currently blocked IPs."""


# ── Mock Implementation (default, safe for demo/PFA) ─────────────────────────
class MockBlocker(FirewallBlocker):
    """Safe mock for demo and testing. Does nothing real."""

    def __init__(self):
        self._blocked = {}

    def block_ip(self, ip: str, reason: str) -> dict:
        self._blocked[ip] = {"reason": reason, "blocked_at": datetime.utcnow().isoformat()}
        logger.info(f"[MOCK] Would block IP {ip} — reason: {reason}")
        return {"status": "simulated", "ip": ip, "action": "block"}

    def unblock_ip(self, ip: str) -> dict:
        self._blocked.pop(ip, None)
        logger.info(f"[MOCK] Would unblock IP {ip}")
        return {"status": "simulated", "ip": ip, "action": "unblock"}

    def list_blocked(self) -> list:
        return list(self._blocked.keys())


# ── pfSense Implementation ────────────────────────────────────────────────────
class PfSenseBlocker(FirewallBlocker):
    """
    Blocks IPs via pfSense REST API (pfSense-API package required).
    Configure via environment variables:
      PFSENSE_URL, PFSENSE_API_KEY, PFSENSE_ALIAS_NAME
    """

    def __init__(self):
        import requests
        self.url = os.environ["PFSENSE_URL"].rstrip("/")
        self.api_key = os.environ["PFSENSE_API_KEY"]
        self.alias = os.getenv("PFSENSE_ALIAS_NAME", "deceptr_blacklist")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })
        self.session.verify = False

    def block_ip(self, ip: str, reason: str) -> dict:
        try:
            resp = self.session.post(
                f"{self.url}/api/v1/firewall/alias/entry",
                json={"name": self.alias, "address": ip, "detail": reason},
                timeout=10,
            )
            resp.raise_for_status()
            logger.warning(f"[PFSENSE] Blocked IP {ip} — reason: {reason}")
            return {"status": "blocked", "ip": ip, "firewall": "pfsense"}
        except Exception as e:
            logger.error(f"[PFSENSE] Failed to block {ip}: {e}")
            return {"status": "error", "ip": ip, "error": str(e)}

    def unblock_ip(self, ip: str) -> dict:
        try:
            resp = self.session.delete(
                f"{self.url}/api/v1/firewall/alias/entry",
                json={"name": self.alias, "address": ip},
                timeout=10,
            )
            resp.raise_for_status()
            return {"status": "unblocked", "ip": ip}
        except Exception as e:
            return {"status": "error", "ip": ip, "error": str(e)}

    def list_blocked(self) -> list:
        try:
            resp = self.session.get(
                f"{self.url}/api/v1/firewall/alias",
                params={"name": self.alias},
                timeout=10,
            )
            data = resp.json()
            return data.get("data", {}).get("address", [])
        except Exception as e:
            logger.error(f"[PFSENSE] list_blocked error: {e}")
            return []


# ── Factory ───────────────────────────────────────────────────────────────────
def get_blocker() -> FirewallBlocker:
    """Returns the appropriate blocker based on FIREWALL_ENABLED env var."""
    enabled = os.getenv("FIREWALL_ENABLED", "false").lower() == "true"
    if not enabled:
        logger.info("[RESPONDER] Firewall blocking DISABLED (MockBlocker active)")
        return MockBlocker()

    provider = os.getenv("FIREWALL_PROVIDER", "pfsense").lower()
    if provider == "pfsense":
        logger.info("[RESPONDER] Using pfSense firewall blocker")
        return PfSenseBlocker()

    logger.warning(f"[RESPONDER] Unknown provider '{provider}', using MockBlocker")
    return MockBlocker()


# ── Module-level singleton ────────────────────────────────────────────────────
_blocker: FirewallBlocker = None


def respond_to_alert(alert: dict) -> dict:
    """
    Synchronous interface — called by pipeline when a CRITICAL alert fires.
    alert = {"risk_level": "CRITICAL", "source_ip": "1.2.3.4", "attack_type": "..."}
    """
    global _blocker
    if _blocker is None:
        _blocker = get_blocker()

    risk = alert.get("risk_level", "").upper()
    ip = alert.get("source_ip", "")

    if not ip:
        return {"status": "skipped", "reason": "no source_ip"}

    if risk == "CRITICAL":
        reason = (
            f"DECEPTR auto-block: {alert.get('attack_type', 'unknown')} "
            f"— {datetime.utcnow().isoformat()}"
        )
        return _blocker.block_ip(ip, reason)

    return {"status": "skipped", "reason": f"risk_level={risk} not CRITICAL"}


# ── Async wrapper for the pipeline main loop ──────────────────────────────────
class Responder:
    """
    Async-compatible wrapper used by pipeline/main.py.
    Keeps the existing pipeline interface while using the new FirewallBlocker.
    """

    def __init__(self):
        self._blocker = get_blocker()
        logger.info(f"[RESPONDER] Initialized ({type(self._blocker).__name__})")

    async def process(self, event: dict, alerts: list) -> None:
        src_ip = event.get("src_ip")
        if not src_ip or src_ip in ALLOWLIST:
            return

        should_block = False
        reason = ""

        for alert in alerts:
            if alert.get("severity") in BLOCK_SEVERITIES:
                should_block = True
                reason = f"Alert {alert.get('severity')} - {alert.get('rule')}"
                break

        if not should_block and event.get("abuse_score", 0) >= BLOCK_MIN_ABUSE_SCORE:
            should_block = True
            reason = f"High Abuse Score ({event.get('abuse_score')})"

        if should_block:
            await asyncio.to_thread(
                self._blocker.block_ip, src_ip, reason
            )
