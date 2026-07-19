"""VNBOT API — Notifications infrastructure."""

from .channels import (
    DeliveryResult,
    DeliveryStatus,
    NotificationChannel,
    WebPushMockChannel,
    get_channel,
    list_channels,
    register_channel,
    register_default_channels,
)

__all__ = [
    "DeliveryResult",
    "DeliveryStatus",
    "NotificationChannel",
    "WebPushMockChannel",
    "get_channel",
    "list_channels",
    "register_channel",
    "register_default_channels",
]
