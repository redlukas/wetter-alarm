"""Custom types for wetter_alarm."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .coordinator import WetterAlarmCoordinator


type WetterAlarmConfigEntry = ConfigEntry[WetterAlarmData]


@dataclass
class WetterAlarmData:
    """Data for the wetter_alarm integration."""

    integration: Integration
    coordinators: list[WetterAlarmCoordinator]
