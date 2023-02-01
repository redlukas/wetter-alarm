from __future__ import annotations

import json
import logging

import requests
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)
alert_url = "https://my.wetteralarm.ch/v7/alarms/meteo.json"


class WetterAlarmApiClient:
    def __init__(self, poi_id):
        self.poi_id = poi_id
        self.poi_url = f"https://my.wetteralarm.ch/v7/pois/{poi_id}.json"
        _LOGGER.error("API instance initialized for poi id", poi_id)

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
            _LOGGER.error("got alerts", parsed)

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
