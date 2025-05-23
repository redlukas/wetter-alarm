"""
Custom integration to integrate wetter_alarm with Home Assistant.

For more details about this integration, please refer to
https://github.com/redlukas/wetter-alarm
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from venv import logger

from homeassistant.const import Platform
from homeassistant.loader import async_get_loaded_integration

from .api import WetterAlarmApiClient
from .data import WetterAlarmData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import WetterAlarmConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: WetterAlarmConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    logger.debug("Setting up entry %s", entry.entry_id)
    logger.debug(entry.data)

    entry.runtime_data = WetterAlarmData(
        integration=async_get_loaded_integration(hass, entry.domain),
    )

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: WetterAlarmConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: WetterAlarmConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
