"""
Custom integration to integrate wetter_alarm with Home Assistant.

For more details about this integration, please refer to
https://github.com/redlukas/wetter-alarm
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.loader import async_get_loaded_integration

from .const import CONFIG_DATA_LANGUAGE, CONFIG_POIS, LOGGER
from .coordinator import WetterAlarmCoordinator
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
    LOGGER.debug("Setting up entry %s", entry.entry_id)

    data_language = entry.data[CONFIG_DATA_LANGUAGE]
    coordinators: list[WetterAlarmCoordinator] = []
    for poi_name, poi_id in entry.data[CONFIG_POIS]:
        coordinator = WetterAlarmCoordinator(
            hass=hass,
            logger=LOGGER,
            poi_id=poi_id,
            poi_name=poi_name,
            data_language=data_language,
        )
        # Perform the initial poll here in the integration setup, *before*
        # forwarding to the platforms. A transient failure then raises
        # ConfigEntryNotReady so HA retries the entry with backoff, instead of
        # the error escaping the forwarded sensor platform (which spams the log
        # and can stall startup).
        await coordinator.async_config_entry_first_refresh()
        coordinators.append(coordinator)

    entry.runtime_data = WetterAlarmData(
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinators=coordinators,
    )

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
    await hass.config_entries.async_reload(entry.entry_id)
