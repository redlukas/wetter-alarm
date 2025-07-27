"""Sensor platform for wetter_alarm."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import (
    DEGREE,
    PERCENTAGE,
    UnitOfLength,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfTime,
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
    POI_name,
)

from .coordinator import WetterAlarmCoordinator
from .entity import WetterAlarmEntity

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data import WetterAlarmConfigEntry
    from .model.poi import POI

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
            WetterAlarmPOINameSensor(
                coordinator, SensorEntityDescription(key=POI_name, name="Name")
            ),
        ]

        sensors.extend(
            WetterAlarmInsolationSensor(
                coordinator,
                SensorEntityDescription(
                    key=f"day_{day}_insolation",
                    name=f"Insolation day {day}",
                    translation_key="insolation",
                ),
                day=day,
            )
            for day in range(6)
        )
        sensors.extend(
            WetterAlarmWindSpeedSensor(
                coordinator,
                SensorEntityDescription(
                    key=f"day_{day}_wind_speed_max",
                    name=f"Maximum wind speed day {day}",
                    translation_key="wind_speed_max",
                ),
                day=day,
            )
            for day in range(6)
        )
        sensors.extend(
            WetterAlarmMaxTemperatureSensor(
                coordinator,
                SensorEntityDescription(
                    key=f"day_{day}_temperature_max",
                    name=f"Maximum Temperature day {day}",
                    translation_key="temperature_max",
                ),
                day=day,
            )
            for day in range(6)
        )
        sensors.extend(
            WetterAlarmMinTemperatureSensor(
                coordinator,
                SensorEntityDescription(
                    key=f"day_{day}_temperature_min",
                    name=f"Minimum Temperature day {day}",
                    translation_key="temperature_min",
                ),
                day=day,
            )
            for day in range(6)
        )
        sensors.extend(
            WetterAlarmPrecipitationAmountSensor(
                coordinator,
                SensorEntityDescription(
                    key=f"day_{day}_precipitation_amount",
                    name=f"Precipitation day {day}",
                    translation_key="precipitation_amount",
                ),
                day=day,
            )
            for day in range(6)
        )
        sensors.extend(
            WetterAlarmPrecipitationProbabilitySensor(
                coordinator,
                SensorEntityDescription(
                    key=f"day_{day}_precipitation_probability",
                    name=f"Precipitation probability day {day}",
                    translation_key="precipitation_probability",
                ),
                day=day,
            )
            for day in range(6)
        )
        sensors.extend(
            WetterAlarmLunarPhaseSensor(
                coordinator,
                SensorEntityDescription(
                    key=f"day_{day}_lunar_phase",
                    name=f"Lunar phase day {day}",
                    translation_key="lunar_phase",
                ),
                day=day,
            )
            for day in range(6)
        )
        sensors.extend(
            WetterAlarmMoodSensor(
                coordinator,
                SensorEntityDescription(
                    key=f"day_{day}_mood",
                    name=f"Mood day {day}",
                    translation_key="mood",
                ),
                day=day,
            )
            for day in range(6)
        )
        sensors.extend(
            WetterAlarmSunriseSensor(
                coordinator,
                SensorEntityDescription(
                    key=f"day_{day}_sunrise",
                    name=f"Sunrise day {day}",
                    translation_key="sunrise",
                ),
                day=day,
            )
            for day in range(6)
        )
        sensors.extend(
            WetterAlarmSunsetSensor(
                coordinator,
                SensorEntityDescription(
                    key=f"day_{day}_sunset",
                    name=f"Sunset day {day}",
                    translation_key="sunset",
                ),
                day=day,
            )
            for day in range(6)
        )
        sensors.extend(
            WetterAlarmMaxInsolationSensor(
                coordinator,
                SensorEntityDescription(
                    key=f"day_{day}_insolation_max",
                    name=f"Maximum insolation day {day}",
                    translation_key="insolation_max",
                ),
                day=day,
            )
            for day in range(6)
        )
        sensors.extend(
            WetterAlarmLunarPhasePercentageSensor(
                coordinator,
                SensorEntityDescription(
                    key=f"day_{day}_lunar_phase_percentage",
                    name=f"Lunar phase percentage day {day}",
                    translation_key="lunar_phase_percentage",
                ),
                day=day,
            )
            for day in range(6)
        )
        sensors.extend(
            WetterAlarmWindDirectionSensor(
                coordinator,
                SensorEntityDescription(
                    key=f"day_{day}_wind_direction",
                    name=f"Wind direction day {day}",
                    translation_key="wind_direction",
                ),
                day=day,
            )
            for day in range(6)
        )
        sensors.extend(
            WetterAlarmDateSensor(
                coordinator,
                SensorEntityDescription(
                    key=f"day_{day}_date",
                    name=f"Date day {day}",
                    translation_key="date",
                ),
                day=day,
            )
            for day in range(6)
        )

        all_sensors.extend(sensors)

    async_add_entities(all_sensors)
    for sensor in all_sensors:
        await sensor.coordinator.async_config_entry_first_refresh()


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
    def available(self) -> bool:
        """Tell the frontend if the sensor is available."""
        return self.coordinator.last_update_success

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, str(self._poi_id))},
            name=self._name,
            manufacturer="Wetter-Alarm",
            model="API",
            sw_version="7",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://www.wetteralarm.ch/",
        )

    @property
    def native_value(self) -> object:
        """Return the native value of the sensor."""
        data: POI = self.coordinator.data
        if data is None:
            return None
        return self.extract_values_from_object(data).get(self.entity_description.key)

    def extract_values_from_object(self, poi: POI) -> dict[str, Any]:
        """Extract values from object."""
        return {
            ALARM_ID: poi.alerts[0].alert_id,
            VALID_FROM: poi.alerts[0].valid_from,
            VALID_TO: poi.alerts[0].valid_to,
            PRIORITY: poi.alerts[0].priority,
            REGION: getattr(poi.alerts[0].region, self.coordinator.data_language).name,
            TITLE: getattr(poi.alerts[0], self.coordinator.data_language).title,
            HINT: getattr(poi.alerts[0], self.coordinator.data_language).hint,
            SIGNATURE: getattr(poi.alerts[0], self.coordinator.data_language).signature,
            POI_name: getattr(poi, self.coordinator.data_language).label,
        }


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


class WetterAlarmPOINameSensor(WetterAlarmBaseSensor):
    """Sensor for the name of a point of interest."""

    _attr_icon = "mdi:form-textbox"


class WetterAlarmInsolationSensor(WetterAlarmBaseSensor):
    """Sensor for the name of a point of interest."""

    def __init__(
        self,
        coordinator: WetterAlarmCoordinator,
        entity_description: SensorEntityDescription,
        day: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator, entity_description=entity_description)
        self.entity_description = entity_description
        self._name = coordinator.name
        self._poi_id = coordinator.get_poi_id
        self._suffix = entity_description.key
        self._day = day

    _attr_icon = "mdi:sun-clock"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.HOURS
    _attr_suggested_display_precision = 1

    @property
    def native_value(self) -> object:
        """Return the native value of the sensor."""
        data: POI = self.coordinator.data
        if data is None:
            return None
        return data.day_forecasts[self._day].insolation


class WetterAlarmMaxWindSpeedSensor(WetterAlarmBaseSensor):
    """Sensor for the name of a point of interest."""

    def __init__(
        self,
        coordinator: WetterAlarmCoordinator,
        entity_description: SensorEntityDescription,
        day: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator, entity_description=entity_description)
        self.entity_description = entity_description
        self._name = coordinator.name
        self._poi_id = coordinator.get_poi_id
        self._suffix = entity_description.key
        self._day = day

    _attr_icon = "mdi:weather-dust"
    _attr_device_class = SensorDeviceClass.SPEED
    _attr_native_unit_of_measurement = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_suggested_display_precision = 0

    @property
    def native_value(self) -> object:
        """Return the native value of the sensor."""
        data: POI = self.coordinator.data
        if data is None:
            return None
        return data.day_forecasts[self._day].wind_speed_max


class WetterAlarmMinTemperatureSensor(WetterAlarmBaseSensor):
    """Sensor for the name of a point of interest."""

    def __init__(
        self,
        coordinator: WetterAlarmCoordinator,
        entity_description: SensorEntityDescription,
        day: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator, entity_description=entity_description)
        self.entity_description = entity_description
        self._name = coordinator.name
        self._poi_id = coordinator.get_poi_id
        self._suffix = entity_description.key
        self._day = day

    _attr_icon = "mdi:thermometer-chevron-down"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_suggested_display_precision = 0

    @property
    def native_value(self) -> object:
        """Return the native value of the sensor."""
        data: POI = self.coordinator.data
        if data is None:
            return None
        return data.day_forecasts[self._day].temperature_min


class WetterAlarmMaxTemperatureSensor(WetterAlarmBaseSensor):
    """Sensor for the name of a point of interest."""

    def __init__(
        self,
        coordinator: WetterAlarmCoordinator,
        entity_description: SensorEntityDescription,
        day: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator, entity_description=entity_description)
        self.entity_description = entity_description
        self._name = coordinator.name
        self._poi_id = coordinator.get_poi_id
        self._suffix = entity_description.key
        self._day = day

    _attr_icon = "mdi:thermometer-chevron-down"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_suggested_display_precision = 0

    @property
    def native_value(self) -> object:
        """Return the native value of the sensor."""
        data: POI = self.coordinator.data
        if data is None:
            return None
        return data.day_forecasts[self._day].temperature_max


class WetterAlarmWindSpeedSensor(WetterAlarmBaseSensor):
    """Sensor for the name of a point of interest."""

    def __init__(
        self,
        coordinator: WetterAlarmCoordinator,
        entity_description: SensorEntityDescription,
        day: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator, entity_description=entity_description)
        self.entity_description = entity_description
        self._name = coordinator.name
        self._poi_id = coordinator.get_poi_id
        self._suffix = entity_description.key
        self._day = day

    _attr_icon = "mdi:weather-dust"
    _attr_device_class = SensorDeviceClass.SPEED
    _attr_native_unit_of_measurement = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_suggested_display_precision = 0

    @property
    def native_value(self) -> object:
        """Return the native value of the sensor."""
        data: POI = self.coordinator.data
        if data is None:
            return None
        return data.day_forecasts[self._day].wind_speed_max


class WetterAlarmPrecipitationAmountSensor(WetterAlarmBaseSensor):
    """Sensor for the name of a point of interest."""

    def __init__(
        self,
        coordinator: WetterAlarmCoordinator,
        entity_description: SensorEntityDescription,
        day: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator, entity_description=entity_description)
        self.entity_description = entity_description
        self._name = coordinator.name
        self._poi_id = coordinator.get_poi_id
        self._suffix = entity_description.key
        self._day = day

    _attr_icon = "mdi:water"
    _attr_device_class = SensorDeviceClass.PRECIPITATION
    _attr_native_unit_of_measurement = UnitOfLength.MILLIMETERS
    _attr_suggested_display_precision = 1

    @property
    def native_value(self) -> object:
        """Return the native value of the sensor."""
        data: POI = self.coordinator.data
        if data is None:
            return None
        return data.day_forecasts[self._day].precipitation_amount


class WetterAlarmPrecipitationProbabilitySensor(WetterAlarmBaseSensor):
    """Sensor for the name of a point of interest."""

    def __init__(
        self,
        coordinator: WetterAlarmCoordinator,
        entity_description: SensorEntityDescription,
        day: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator, entity_description=entity_description)
        self.entity_description = entity_description
        self._name = coordinator.name
        self._poi_id = coordinator.get_poi_id
        self._suffix = entity_description.key
        self._day = day

    _attr_icon = "mdi:cloud-percent-outline"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_suggested_display_precision = 0

    @property
    def native_value(self) -> object:
        """Return the native value of the sensor."""
        data: POI = self.coordinator.data
        if data is None:
            return None
        return data.day_forecasts[self._day].precipitation_probability


class WetterAlarmLunarPhaseSensor(WetterAlarmBaseSensor):
    """Sensor for the name of a point of interest."""

    def __init__(
        self,
        coordinator: WetterAlarmCoordinator,
        entity_description: SensorEntityDescription,
        day: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator, entity_description=entity_description)
        self.entity_description = entity_description
        self._name = coordinator.name
        self._poi_id = coordinator.get_poi_id
        self._suffix = entity_description.key
        self._day = day

    _attr_icon = "mdi:moon-waning-crescent"

    @property
    def native_value(self) -> object:
        """Return the native value of the sensor."""
        data: POI = self.coordinator.data
        if data is None:
            return None
        return data.day_forecasts[self._day].lunar_phase


class WetterAlarmMoodSensor(WetterAlarmBaseSensor):
    """Sensor for the name of a point of interest."""

    def __init__(
        self,
        coordinator: WetterAlarmCoordinator,
        entity_description: SensorEntityDescription,
        day: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator, entity_description=entity_description)
        self.entity_description = entity_description
        self._name = coordinator.name
        self._poi_id = coordinator.get_poi_id
        self._suffix = entity_description.key
        self._day = day

    _attr_icon = "mdi:weather-windy-variant"

    @property
    def native_value(self) -> object:
        """Return the native value of the sensor."""
        data: POI = self.coordinator.data
        if data is None:
            return None
        return data.day_forecasts[self._day].mood


class WetterAlarmSunriseSensor(WetterAlarmBaseSensor):
    """Sensor for the name of a point of interest."""

    def __init__(
        self,
        coordinator: WetterAlarmCoordinator,
        entity_description: SensorEntityDescription,
        day: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator, entity_description=entity_description)
        self.entity_description = entity_description
        self._name = coordinator.name
        self._poi_id = coordinator.get_poi_id
        self._suffix = entity_description.key
        self._day = day

    _attr_icon = "mdi:weather-sunset-up"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_state_class = None

    @property
    def native_value(self) -> object:
        """Return the native value of the sensor."""
        data: POI = self.coordinator.data
        if data is None:
            return None
        return data.day_forecasts[self._day].sunrise


class WetterAlarmSunsetSensor(WetterAlarmBaseSensor):
    """Sensor for the name of a point of interest."""

    def __init__(
        self,
        coordinator: WetterAlarmCoordinator,
        entity_description: SensorEntityDescription,
        day: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator, entity_description=entity_description)
        self.entity_description = entity_description
        self._name = coordinator.name
        self._poi_id = coordinator.get_poi_id
        self._suffix = entity_description.key
        self._day = day

    _attr_icon = "mdi:weather-sunset-down"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_state_class = None

    @property
    def native_value(self) -> object:
        """Return the native value of the sensor."""
        data: POI = self.coordinator.data
        if data is None:
            return None
        return data.day_forecasts[self._day].sunset


class WetterAlarmMaxInsolationSensor(WetterAlarmBaseSensor):
    """Sensor for the name of a point of interest."""

    def __init__(
        self,
        coordinator: WetterAlarmCoordinator,
        entity_description: SensorEntityDescription,
        day: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator, entity_description=entity_description)
        self.entity_description = entity_description
        self._name = coordinator.name
        self._poi_id = coordinator.get_poi_id
        self._suffix = entity_description.key
        self._day = day

    _attr_icon = "mdi:theme-light-dark"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.HOURS
    _attr_suggested_display_precision = 0

    @property
    def native_value(self) -> object:
        """Return the native value of the sensor."""
        data: POI = self.coordinator.data
        if data is None:
            return None
        return data.day_forecasts[self._day].insolation_max


class WetterAlarmLunarPhasePercentageSensor(WetterAlarmBaseSensor):
    """Sensor for the name of a point of interest."""

    def __init__(
        self,
        coordinator: WetterAlarmCoordinator,
        entity_description: SensorEntityDescription,
        day: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator, entity_description=entity_description)
        self.entity_description = entity_description
        self._name = coordinator.name
        self._poi_id = coordinator.get_poi_id
        self._suffix = entity_description.key
        self._day = day

    _attr_icon = "mdi:moon-waxing-crescent"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_suggested_display_precision = 0

    @property
    def native_value(self) -> object:
        """Return the native value of the sensor."""
        data: POI = self.coordinator.data
        if data is None:
            return None
        return data.day_forecasts[self._day].lunar_phase_percentage


class WetterAlarmWindDirectionSensor(WetterAlarmBaseSensor):
    """Sensor for the name of a point of interest."""

    def __init__(
        self,
        coordinator: WetterAlarmCoordinator,
        entity_description: SensorEntityDescription,
        day: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator, entity_description=entity_description)
        self.entity_description = entity_description
        self._name = coordinator.name
        self._poi_id = coordinator.get_poi_id
        self._suffix = entity_description.key
        self._day = day

    _attr_icon = "mdi:compass-rose"
    _attr_native_unit_of_measurement = DEGREE
    _attr_suggested_display_precision = 0

    @property
    def native_value(self) -> object:
        """Return the native value of the sensor."""
        data: POI = self.coordinator.data
        if data is None:
            return None
        return data.day_forecasts[self._day].wind_speed_max


class WetterAlarmDateSensor(WetterAlarmBaseSensor):
    """Sensor for the name of a point of interest."""

    def __init__(
        self,
        coordinator: WetterAlarmCoordinator,
        entity_description: SensorEntityDescription,
        day: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator, entity_description=entity_description)
        self.entity_description = entity_description
        self._name = coordinator.name
        self._poi_id = coordinator.get_poi_id
        self._suffix = entity_description.key
        self._day = day

    _attr_icon = "mdi:calendar-month"
    _attr_device_class = SensorDeviceClass.DATE

    @property
    def native_value(self) -> object:
        """Return the native value of the sensor."""
        data: POI = self.coordinator.data
        if data is None:
            return None
        return data.day_forecasts[self._day].date
