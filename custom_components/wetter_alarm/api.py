from __future__ import annotations

import json
import logging
import socket
from datetime import datetime
from typing import Any

import aiohttp
import async_timeout
from homeassistant.exceptions import HomeAssistantError

from .const import (
    ALARM_ID,
    HINT,
    PRIORITY,
    REGION,
    SIGNATURE,
    TITLE,
    VALID_FROM,
    VALID_TO,
)

_LOGGER = logging.getLogger(__name__)
# api_base_url = "https://my.wetteralarm.ch"
api_base_url = "https://sta.my.wetteralarm.ch"
alert_url = f"{api_base_url}/v7/alarms/meteo.json"


class WetterAlarmApiClient:
    def __init__(self, poi_id: int, data_language: str = "en"):
        self.poi_id = poi_id
        self.poi_url = f"{api_base_url}/v7/pois/{poi_id}.json"
        self.data_language = data_language or "en"

    async def async_validate_poi_id(self) -> bool:
        try:
            res = await self._api_wrapper("get", self.poi_url)
            if res:
                return True
            raise WetterAlarmApiError(
                poi_id=str(self.poi_id),
                msg=f"Poi {self.poi_id} did not return a valid response",
            )
        except CannotConnect as er:
            _LOGGER.error("error validating the poi id", er)
            raise WetterAlarmApiError(
                poi_id=str(self.poi_id),
                msg=f"Poi {self.poi_id} did not return a valid response",
            )

    async def async_get_poi_data(self):
        try:
            res = await self._api_wrapper("get", self.poi_url)
            _LOGGER.error(f"got info for POI {res}")
        except json.decoder.JSONDecodeError:
            _LOGGER.error(f"Poi {self.poi_id} did not return a valid JSON")
        except (ValueError, KeyError) as e:
            _LOGGER.exception("did not satisfy expectations: %s", self.poi_id, e)

    async def async_search_for_alerts(self):
        try:
            res = await self._api_wrapper("get", alert_url)

            meteo_alarms = res["meteo_alarms"]

            found_alarm = False
            for alarm in meteo_alarms:
                if self.poi_id in alarm["poi_ids"]:
                    _LOGGER.debug(
                        f"found alarm for {self.poi_id} in {self.data_language}"
                    )
                    return {
                        ALARM_ID: alarm["id"],
                        VALID_FROM: datetime.strptime(
                            alarm["valid_from"], "%Y-%m-%dT%H:%M:%S.%fZ"
                        ),
                        VALID_TO: datetime.strptime(
                            alarm["valid_to"], "%Y-%m-%dT%H:%M:%S.%fZ"
                        ),
                        PRIORITY: alarm["priority"],
                        REGION: alarm["region"][self.data_language]["name"],
                        TITLE: alarm[self.data_language]["title"],
                        HINT: alarm[self.data_language]["hint"],
                        SIGNATURE: alarm[self.data_language]["signature"],
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

        except json.decoder.JSONDecodeError:
            _LOGGER.error(f"Poi {self.poi_id} did not return a valid JSON")
        except (ValueError, KeyError) as e:
            _LOGGER.error("did not satisfy expectations:", self.poi_id, e)

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method=method,
                        url=url,
                        headers=headers,
                        json=data,
                    ) as response:
                        return await response.json()

        except TimeoutError as exception:
            raise CannotConnect(
                f"Timeout error fetching information - {exception}"
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise CannotConnect(
                f"Error fetching information - {exception}"
            ) from exception
        except Exception as exception:
            raise CannotConnect(
                f"Something really wrong happened! - {exception}"
            ) from exception


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
        return f"<Wetteralarm API Error sta:{self.poi_id} message:{self.msg}>"
