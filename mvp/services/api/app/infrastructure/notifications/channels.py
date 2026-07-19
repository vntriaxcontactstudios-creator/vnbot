"""VNBOT API — Notification channels.

NotificationChannel Protocol + WebPushMock implementation.

The Protocol is the contract — any new channel (web_push, email, telegram, etc.)
must implement it. This keeps the scheduler decoupled from delivery details.

Per docs/03-ESQUEMA-BACKEND-VNBOT.md §14:
- Delivery worker: take job → verify occurrence still active → verify not delivered
  → check silence window → select channel → send → record → retry if temporal error.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Protocol, runtime_checkable

from ..db.models import Notification

logger = logging.getLogger("vnbot.api.notifications")


class DeliveryStatus(str, Enum):
    """Outcome of a delivery attempt."""

    DELIVERED = "delivered"
    TEMPORARY_FAILURE = "temporary_failure"  # retry later
    PERMANENT_FAILURE = "permanent_failure"  # do not retry
    SKIPPED = "skipped"  # silence window / cancelled


@dataclass
class DeliveryResult:
    """Result of a notification delivery attempt."""

    status: DeliveryStatus
    provider_message_id: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    response_metadata: dict | None = None


@runtime_checkable
class NotificationChannel(Protocol):
    """Contract for notification delivery channels.

    Implementations: WebPushMock (0.1), WebPush (0.4), Email (0.8), Telegram (0.8).
    """

    @property
    def name(self) -> str:
        """Channel identifier (e.g. 'mock', 'web_push', 'email')."""
        ...

    async def send(self, notification: Notification) -> DeliveryResult:
        """Send the notification. Returns delivery result.

        Must be idempotent: same notification.id sent twice should not deliver twice.
        Implementations should check the notification.status before sending.
        """
        ...

    async def healthcheck(self) -> bool:
        """Return True if the channel is healthy and ready to send."""
        ...


class WebPushMockChannel:
    """Mock notification channel for Phase 0.1.

    Persists notifications to the database (status: delivered) without actually
    sending anything. Used in development and tests.

    This is the default channel per Terreno Preparado §2.4 (Phase 0.1 = mock).
    """

    def __init__(self) -> None:
        pass

    @property
    def name(self) -> str:
        return "mock"

    async def send(self, notification: Notification) -> DeliveryResult:
        """Mock-send: just mark as delivered in DB."""
        # Idempotency: if already delivered, skip
        if notification.status == "delivered":
            logger.info(
                f"Notification {notification.id} already delivered, skipping (idempotent)"
            )
            return DeliveryResult(
                status=DeliveryStatus.SKIPPED,
                error_code="already_delivered",
                error_message="Notification was already delivered",
            )

        try:
            # In a real channel, here we'd call the provider API (FCM, APNs, etc.)
            # For mock, we just mark as delivered
            notification.status = "delivered"
            notification.updated_at = datetime.now(timezone.utc)

            logger.info(
                f"[MOCK] Notification delivered: id={notification.id} "
                f"title='{notification.title}'"
            )

            return DeliveryResult(
                status=DeliveryStatus.DELIVERED,
                provider_message_id=f"mock-{notification.id}",
                response_metadata={
                    "channel": "mock",
                    "delivered_at": notification.updated_at.isoformat(),
                },
            )

        except Exception as e:
            logger.error(f"Mock delivery failed for {notification.id}: {e}")
            return DeliveryResult(
                status=DeliveryStatus.PERMANENT_FAILURE,
                error_code=type(e).__name__,
                error_message=str(e),
            )

    async def healthcheck(self) -> bool:
        """Mock channel is always healthy (it's just DB writes)."""
        return True


# ──────────────────────────────────────────────────────────────────────────────
# Channel registry
# ──────────────────────────────────────────────────────────────────────────────


_CHANNELS: dict[str, NotificationChannel] = {}


def register_channel(channel: NotificationChannel) -> None:
    """Register a notification channel. Idempotent."""
    _CHANNELS[channel.name] = channel
    logger.info(f"Registered notification channel: {channel.name}")


def get_channel(name: str) -> NotificationChannel | None:
    """Look up a registered channel by name."""
    return _CHANNELS.get(name)


def list_channels() -> list[str]:
    """List all registered channel names."""
    return list(_CHANNELS.keys())


def register_default_channels() -> None:
    """Register the default channels for Phase 0.1."""
    if "mock" not in _CHANNELS:
        register_channel(WebPushMockChannel())
