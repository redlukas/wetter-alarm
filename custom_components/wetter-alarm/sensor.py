"""Platform for sensor integration."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import ALARM_ID
from .const import DOMAIN
from .const import HINT
from .const import PRIORITY
from .const import REGION
from .const import SIGNATURE
from .const import TITLE
from .const import VALID_FROM
from .const import VALID_TO
from .wetter_alarm_client import WetterAlarmApiClient

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=60)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    pois_from_config = config_entry.data["pois"]
    all_sensors = []
    for poi_name, poi_id in pois_from_config:
        coordinator = WetterAlarmCoordinator(
            hass=hass, logger=_LOGGER, poi_name=poi_name, poi_id=poi_id
        )
        sensors = [
            WetterAlarmIdSensor(coordinator, ALARM_ID),
            WetterAlarmValidFromSensor(coordinator, VALID_FROM),
            WetterAlarmValidToSensor(coordinator, VALID_TO),
            WetterAlarmPrioritySensor(coordinator, PRIORITY),
            WetterAlarmRegionSensor(coordinator, REGION),
            WetterAlarmTitleSensor(coordinator, TITLE),
            WetterAlarmHintSensor(coordinator, HINT),
            WetterAlarmSignatureSensor(coordinator, SIGNATURE),
        ]
        all_sensors.extend(sensors)
        await coordinator.async_config_entry_first_refresh()
    async_add_entities(all_sensors)


class WetterAlarmBaseSensor(CoordinatorEntity, SensorEntity):
    """base Wetter-Alarm Sensor, all sensors inherit from it"""

    def __init__(self, coordinator: WetterAlarmCoordinator, suffix: str):
        SensorEntity.__init__(self)
        CoordinatorEntity.__init__(self, coordinator)
        self._name = coordinator.name
        self._suffix = suffix
        self._poi_id = coordinator.get_poi_id
        _LOGGER.debug(f"created Sensor of class {__class__} with uid {self.unique_id}")

    _attr_has_entity_name: True
    _attr_should_poll: True

    @property
    def name(self) -> str | None:
        return f"{self._name} {self._suffix}"

    @property
    def friendly_name(self) -> str | None:
        return f"{self._name} {self._suffix.replace('_', ' ').capitalize()}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        info = DeviceInfo(
            identifiers={(DOMAIN, str(self._poi_id))},
            name=f"Point of Interest-{self._name}/{self._poi_id}",
            default_manufacturer="Wetter-Alarm",
            default_model="API",
        )
        return info

    @property
    def unique_id(self) -> str | None:
        return f"Point of Interest - {self._poi_id} - {self._suffix}"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        value = self.coordinator.data[self._suffix]
        self._attr_native_value = value
        self.async_write_ha_state()


class WetterAlarmIdSensor(WetterAlarmBaseSensor):
    """Sensor for the Alarm ID"""

    _attr_icon = "mdi:identifier"


class WetterAlarmValidFromSensor(WetterAlarmBaseSensor):
    """Sensor for when the alarm starts"""

    _attr_icon = "mdi:calendar-arrow-left"
    _attr_device_class = SensorDeviceClass.DATE


class WetterAlarmValidToSensor(WetterAlarmBaseSensor):
    """Sensor for when the alarm ends"""

    _attr_icon = "mdi:calendar-arrow-right"
    _attr_device_class = SensorDeviceClass.DATE


class WetterAlarmPrioritySensor(WetterAlarmBaseSensor):
    """Sensor for the Alarm priority"""

    _attr_icon = "mdi:chevron-triple-up"


class WetterAlarmRegionSensor(WetterAlarmBaseSensor):
    """Sensor for the region the alarm occurs in"""

    _attr_icon = "mdi:map-marker-check-outline"


class WetterAlarmTitleSensor(WetterAlarmBaseSensor):
    """Sensor for the title of the Alarm"""

    _attr_icon = "mdi:format-title"


class WetterAlarmHintSensor(WetterAlarmBaseSensor):
    """Sensor for the Alarm hint"""

    _attr_icon = "mdi:account-alert"


class WetterAlarmSignatureSensor(WetterAlarmBaseSensor):
    """Sensor for who issued the alarm"""

    _attr_icon = "mdi:signature-freehand"


class WetterAlarmCoordinator(DataUpdateCoordinator):
    """Custom Wetter-Alarm Coordinator"""

    def __init__(
        self, hass: HomeAssistant, logger: logging.Logger, poi_id: int, poi_name: str
    ) -> None:
        self._hass = hass
        self._poi_id = poi_id
        self._name = f"{poi_name}"
        self._logger = logger

        super().__init__(
            hass=hass,
            logger=logger,
            name=self._name,
            update_interval=SCAN_INTERVAL,
        )

    @property
    def get_hass(self):
        return self._hass

    @property
    def get_poi_id(self):
        return self._poi_id

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint.
        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """

        self.update_interval = SCAN_INTERVAL

        async def fetch_all_values() -> dict[str, float]:
            client = WetterAlarmApiClient(self._poi_id)
            data = await client.search_for_alerts_async(hass=self._hass)
            return data

        return await fetch_all_values()
