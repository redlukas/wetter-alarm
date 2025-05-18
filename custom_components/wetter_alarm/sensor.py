"""Sensor platform for wetter_alarm."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

from custom_components.wetter_alarm.const import (
    ALARM_ID,
    CONFIG_DATA_LANGUAGE,
    CONFIG_POIS,
    DOMAIN,
    HINT,
    PRIORITY,
    REGION,
    SIGNATURE,
    TITLE,
    VALID_FROM,
    VALID_TO,
)

from .coordinator import WetterAlarmCoordinator
from .entity import WetterAlarmEntity

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data import WetterAlarmConfigEntry

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="wetter_alarm",
        name="Integration Sensor",
        icon="mdi:format-quote-close",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: WetterAlarmConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    pois_from_config = config_entry.data[CONFIG_POIS]
    data_language = config_entry.data[CONFIG_DATA_LANGUAGE]
    all_sensors = []
    for poi_name, poi_id in pois_from_config:
        coordinator = WetterAlarmCoordinator(
            hass=hass,
            logger=_LOGGER,
            poi_name=poi_name,
            poi_id=poi_id,
            data_language=data_language,
        )

        sensors = [
            WetterAlarmIdSensor(
                coordinator, SensorEntityDescription(key=ALARM_ID, name="Alarm ID")
            ),
            WetterAlarmValidFromSensor(
                coordinator, SensorEntityDescription(key=VALID_FROM, name="Valid From")
            ),
            WetterAlarmValidToSensor(
                coordinator, SensorEntityDescription(key=VALID_TO, name="Valid To")
            ),
            WetterAlarmPrioritySensor(
                coordinator, SensorEntityDescription(key=PRIORITY, name="Priority")
            ),
            WetterAlarmRegionSensor(
                coordinator, SensorEntityDescription(key=REGION, name="Region")
            ),
            WetterAlarmTitleSensor(
                coordinator, SensorEntityDescription(key=TITLE, name="Title")
            ),
            WetterAlarmHintSensor(
                coordinator, SensorEntityDescription(key=HINT, name="Hint")
            ),
            WetterAlarmSignatureSensor(
                coordinator, SensorEntityDescription(key=SIGNATURE, name="Signature")
            ),
        ]

        all_sensors.extend(sensors)

        await coordinator.async_config_entry_first_refresh()

    async_add_entities(all_sensors)


class WetterAlarmBaseSensor(WetterAlarmEntity, SensorEntity):
    """wetter_alarm Sensor class."""

    def __init__(
        self,
        coordinator: WetterAlarmCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize a WetterAlarmBaseSensor with coordinator and entity description."""  # noqa: E501
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._name = coordinator.name
        self._poi_id = coordinator.get_poi_id
        self._suffix = entity_description.key

    _attr_has_entity_name: True
    _attr_should_poll: True

    @property
    def name(self) -> str | None:
        """Return the name of the sensor."""
        return f"{self._name} {self._suffix}"

    @property
    def friendly_name(self) -> str | None:
        """Return the friendly name for this sensor."""
        return f"{self._name} {self._suffix.replace('_', ' ').capitalize()}"

    @property
    def unique_id(self) -> str | None:
        """Return a unique ID for this sensor."""
        return f"Point of Interest - {self._poi_id} - {self._suffix}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, str(self._poi_id))},
            name=f"Point of Interest - {self._name} ({self._poi_id})",
            manufacturer="Wetter-Alarm",
            model="API",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://www.wetteralarm.ch/",
        )

    @property
    def native_value(self) -> object:
        """Return the native value of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self.entity_description.key)


class WetterAlarmIdSensor(WetterAlarmBaseSensor):
    """Sensor for the Alarm ID."""

    _attr_icon = "mdi:identifier"


class WetterAlarmValidFromSensor(WetterAlarmBaseSensor):
    """Sensor for when the alarm starts."""

    _attr_icon = "mdi:calendar-arrow-left"
    _attr_device_class = SensorDeviceClass.DATE


class WetterAlarmValidToSensor(WetterAlarmBaseSensor):
    """Sensor for when the alarm ends."""

    _attr_icon = "mdi:calendar-arrow-right"
    _attr_device_class = SensorDeviceClass.DATE


class WetterAlarmPrioritySensor(WetterAlarmBaseSensor):
    """Sensor for the Alarm priority."""

    _attr_icon = "mdi:chevron-triple-up"


class WetterAlarmRegionSensor(WetterAlarmBaseSensor):
    """Sensor for the region the alarm occurs in."""

    _attr_icon = "mdi:map-marker-check-outline"


class WetterAlarmTitleSensor(WetterAlarmBaseSensor):
    """Sensor for the title of the Alarm."""

    _attr_icon = "mdi:format-title"


class WetterAlarmHintSensor(WetterAlarmBaseSensor):
    """Sensor for the Alarm hint."""

    _attr_icon = "mdi:account-alert"


class WetterAlarmSignatureSensor(WetterAlarmBaseSensor):
    """Sensor for who issued the alarm."""

    _attr_icon = "mdi:signature-freehand"
