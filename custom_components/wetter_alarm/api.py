"""API client for interacting with the WetterAlarm weather alert service."""

from __future__ import annotations

import json
import logging
import socket
from datetime import UTC, datetime
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
api_base_url = "https://my.wetteralarm.ch"
alert_url = f"{api_base_url}/v7/alarms/meteo.json"


class WetterAlarmApiClient:
    """Client for interacting with the WetterAlarm API."""

    def __init__(self, poi_id: int, data_language: str = "en") -> None:
        """Initialize the WetterAlarmApiClient with a POI ID and data language."""
        self.poi_id = poi_id
        self.poi_url = f"{api_base_url}/v7/pois/{poi_id}.json"
        self.data_language = data_language or "en"

    async def async_validate_poi_id(self) -> bool:
        """Validate the POI ID by making a request to the WetterAlarm API."""
        try:
            res = await self._api_wrapper("get", self.poi_url)
            if res:
                return True
            raise WetterAlarmApiError(
                poi_id=str(self.poi_id),
                msg=f"POI {self.poi_id} did not return a valid response",
            )
        except CannotConnectError:
            _LOGGER.exception("error validating the POI %s", self.poi_id)
            raise WetterAlarmApiError(
                poi_id=str(self.poi_id),
                msg=f"POI {self.poi_id} did not return a valid response",
            ) from None

    async def async_search_for_alerts(self) -> dict | None:
        """Search for weather alerts related to the current POI."""
        try:
            res = await self._api_wrapper("get", alert_url)

            meteo_alarms = res.get("meteo_alarms")

            found_alarm = False
            for alarm in meteo_alarms:
                if self.poi_id in alarm["poi_ids"]:
                    _LOGGER.debug(
                        "found alarm for %i in %s", self.poi_id, self.data_language
                    )

                    return {
                        ALARM_ID: alarm.get("id"),
                        VALID_FROM: datetime.strptime(
                            alarm.get("valid_from"), "%Y-%m-%dT%H:%M:%S.%fZ"
                        ).replace(tzinfo=UTC),
                        VALID_TO: datetime.strptime(
                            alarm.get("valid_to"), "%Y-%m-%dT%H:%M:%S.%fZ"
                        ).replace(tzinfo=UTC),
                        PRIORITY: alarm.get("priority"),
                        REGION: alarm.get("region")[self.data_language].get("name"),
                        TITLE: alarm[self.data_language].get("title"),
                        HINT: alarm[self.data_language].get("hint"),
                        SIGNATURE: alarm[self.data_language].get("signature"),
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
            _LOGGER.exception("POI %i did not return a valid JSON", self.poi_id)
        except (ValueError, KeyError):
            _LOGGER.exception("did not satisfy expectations for POI %i", self.poi_id)

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            async with (
                async_timeout.timeout(10),
                aiohttp.ClientSession() as session,
                session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                ) as response,
            ):
                return await response.json()

        except TimeoutError as exception:
            message = "Timeout error fetching information"
            raise CannotConnectError(message, exception) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            message = "Error fetching information"
            raise CannotConnectError(message, exception) from exception


class CannotConnectError(HomeAssistantError):
    """Error to indicate we cannot connect."""

    def __init__(
        self,
        message: str = "Cannot connect",
        original_exception: Exception | None = None,
    ) -> None:
        """Initialize CannotConnectError with an optional message and original exception."""  # noqa: E501
        super().__init__(message)
        self.message = message
        self.original_exception = original_exception

    def __str__(self) -> str:
        """Return a string representation of the error."""
        if self.original_exception:
            return f"{self.message}: {self.original_exception}"
        return self.message


class InvalidAuthError(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class WetterAlarmApiError(HomeAssistantError):
    """Generic API errors."""

    def __init__(self, poi_id: str, msg: str | None = None) -> None:
        """sta: status code, msg: message."""
        HomeAssistantError.__init__(self)
        self.poi_id = poi_id
        self.msg = msg

    def __str__(self) -> str:
        """Return a string representation of the WetterAlarmApiError."""
        return f"<Wetteralarm API Error sta:{self.poi_id} message:{self.msg}>"
