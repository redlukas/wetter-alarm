"""Custom types for wetter_alarm."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration


type WetterAlarmConfigEntry = ConfigEntry[WetterAlarmData]


@dataclass
class WetterAlarmData:
    """Data for the Blueprint integration."""

    integration: Integration
