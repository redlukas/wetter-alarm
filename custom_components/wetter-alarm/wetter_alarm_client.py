from __future__ import annotations

import json
import logging
from datetime import datetime

import requests
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import ALARM_ID
from .const import HINT
from .const import PRIORITY
from .const import REGION
from .const import SIGNATURE
from .const import TITLE
from .const import VALID_FROM
from .const import VALID_TO

_LOGGER = logging.getLogger(__name__)
alert_url = "https://my.wetteralarm.ch/v7/alarms/meteo.json"


class WetterAlarmApiClient:
    def __init__(self, poi_id: int):
        self.poi_id = poi_id
        self.poi_url = f"https://my.wetteralarm.ch/v7/pois/{poi_id}.json"

    def validate_poi_id_sync(self) -> bool:
        try:
            res = requests.get(self.poi_url)
            if res:
                return True
            else:
                return False
        except requests.exceptions as er:
            _LOGGER.error("error validating the poi id", er)
            return False

    async def validate_poi_id_async(self, hass: HomeAssistant) -> bool:
        result = await hass.async_add_executor_job(self.validate_poi_id_sync)
        return result

    def get_poi_data_sync(self):
        try:
            res = requests.get(self.poi_url)
            _LOGGER.error("got info for POI ", res.text)
        except requests.exceptions.ConnectionError as ce:
            _LOGGER.error("generic connection error", ce)
            raise CannotConnect
        except json.decoder.JSONDecodeError:
            _LOGGER.error(f"Poi {self.poi_id} did not return a valid JSON")
        except (ValueError, KeyError) as e:
            _LOGGER.error("did not satisfy expectations:", self.poi_id, e)

    async def get_poi_data_async(self, hass: HomeAssistant):
        result = await hass.async_add_executor_job(self.get_poi_data_sync)
        return result

    def search_for_alerts_sync(self):
        try:
            res = requests.get(alert_url)
            parsed = json.loads(res.text)["meteo_alarms"]
            # _LOGGER.error(f"got alerts {parsed}")

            found_alarm = False
            for alarm in parsed:
                if self.poi_id in alarm["poi_ids"]:
                    return {
                        ALARM_ID: alarm["id"],
                        VALID_FROM: datetime.strptime(
                            alarm["valid_from"], "%Y-%m-%dT%H:%M:%S.%fZ"
                        ),
                        VALID_TO: datetime.strptime(
                            alarm["valid_to"], "%Y-%m-%dT%H:%M:%S.%fZ"
                        ),
                        PRIORITY: alarm["priority"],
                        REGION: alarm["region"]["en"]["name"],
                        TITLE: alarm["en"]["title"],
                        HINT: alarm["en"]["hint"],
                        SIGNATURE: alarm["en"]["signature"],
                    }
            if not found_alarm:
                return {
                    ALARM_ID: -1,
                    VALID_FROM: None,
                    VALID_TO: None,
                    PRIORITY: None,
                    REGION: None,
                    TITLE: None,
                    HINT: None,
                    SIGNATURE: None,
                }

        except requests.exceptions.ConnectionError as ce:
            _LOGGER.error("generic connection error", ce)
            raise CannotConnect
        except json.decoder.JSONDecodeError:
            _LOGGER.error(f"Poi {self.poi_id} did not return a valid JSON")
        except (ValueError, KeyError) as e:
            _LOGGER.error("did not satisfy expectations:", self.poi_id, e)

    async def search_for_alerts_async(self, hass: HomeAssistant):
        result = await hass.async_add_executor_job(self.search_for_alerts_sync)
        return result


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class WetterAlarmApiError(HomeAssistantError):
    """Generic API errors"""

    def __init__(self, poi_id: str, msg: str | None = None) -> None:
        """sta: status code, msg: message"""
        Exception.__init__(self)
        self.poi_id = poi_id
        self.msg = msg

    def __str__(self):
        return f"<Emu API Error sta:{self.poi_id} message:{self.msg}>"
