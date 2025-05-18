"""Coordinator for wetter_alarm."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    WetterAlarmApiClient,
    WetterAlarmApiError,
)

SCAN_INTERVAL = timedelta(seconds=60)

if TYPE_CHECKING:
    import logging

    from homeassistant.core import HomeAssistant

    from .data import WetterAlarmConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class WetterAlarmCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: WetterAlarmConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        poi_id: int,
        poi_name: str,
        data_language: str = "en",
    ) -> None:
        """
        Initialize the WetterAlarmCoordinator.

        Args:
            hass: HomeAssistant instance.
            logger: Logger instance.
            poi_id: Point of Interest ID.
            poi_name: Name of the Point of Interest.
            data_language: Language for data retrieval (default is "en").

        """
        self._hass = hass
        self._poi_id = poi_id
        self._data_language = data_language
        self._name = f"{poi_name}"
        self._logger = logger

        super().__init__(
            hass=hass,
            logger=logger,
            name=self._name,
            update_interval=SCAN_INTERVAL,
        )

    @property
    def get_hass(self) -> HomeAssistant:
        """Return the HomeAssistant instance."""
        return self._hass

    @property
    def get_poi_id(self) -> int:
        """Return the POI (Point of Interest) ID."""
        return self._poi_id

    async def _async_update_data(self) -> Any:
        """
        Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        self.update_interval = SCAN_INTERVAL

        async def fetch_all_values() -> dict[str, Any] | None:
            client = WetterAlarmApiClient(self._poi_id, self._data_language)
            return await client.async_search_for_alerts()

        try:
            return await fetch_all_values()
        except WetterAlarmApiError as exception:
            raise UpdateFailed(exception) from exception
