"""API client for interacting with the WetterAlarm weather alert service."""

from __future__ import annotations

import json
import logging
import socket
from typing import Any

import aiohttp
import async_timeout
from homeassistant.exceptions import HomeAssistantError
from pydantic import ValidationError

from .model.alert import Alert
from .model.poi import POI, LivecamPoi

_LOGGER = logging.getLogger(__name__)
api_base_url = "https://my.wetteralarm.ch"
alert_url = f"{api_base_url}/v7/alarms/meteo.json"


async def _api_wrapper(
    method: str,
    url: str,
    data: dict | None = None,
    headers: dict | None = None,
) -> dict[str, Any]:
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
            res = await _api_wrapper("get", self.poi_url)
            try:
                if res.get("id"):
                    POI.model_validate(res)
                    return True
                LivecamPoi.model_validate(res)
                msg = "Livecam only POIs are unsupported"
                raise WetterAlarmApiError(msg)
            except ValidationError as e:
                msg = f"POI {self.poi_id} did not return a valid response"
                _LOGGER.exception("[%s] ❌ Validation error", self.poi_id)
                raise WetterAlarmApiError(poi_id=str(self.poi_id), msg=msg) from e
        except CannotConnectError:
            msg = f"POI {self.poi_id} did not return a valid response"
            _LOGGER.exception("Error validating the POI %s", self.poi_id)
            raise WetterAlarmApiError(poi_id=str(self.poi_id), msg=msg) from None

    async def _search_for_alerts(self) -> list[Alert] | None:
        """Search for weather alerts related to the current POI."""
        try:
            res = await _api_wrapper("get", alert_url)

            meteo_alarms = [
                Alert.model_validate(raw_alert) for raw_alert in res.get("meteo_alarms")
            ]

            found_alarms = [
                Alert.model_validate_json(
                    """
                {
                    "id": 111,
                    "valid_from": "1970-01-01T00:00:00.000Z",
                    "valid_to": "1970-01-01T01:00:00.000Z",
                    "priority": 99,
                    "region": {
                        "srf_id": 99,
                        "de": { "name": "Bärn" },
                        "fr": { "name": "" },
                        "it": { "name": "" },
                        "en": { "name": "" }
                    },
                    "cantons": [],
                    "poi_ids": [],
                    "code": 2,
                    "de": {
                        "title": "Dummy alert - DE",
                        "hint": "dummy hint - DE",
                        "signature": "dummy signature - DE",
                        "paragraph": ""
                    },
                    "fr": {
                        "title": "Dummy alert - FR",
                        "hint": "dummy hint - FR",
                        "signature": "dummy signature - FR",
                        "paragraph": ""
                    },
                    "it": {
                        "title": "Dummy alert - IT",
                        "hint": "dummy hint - IT",
                        "signature": "dummy signature - IT",
                        "paragraph": ""
                    },
                    "en": {
                        "title": "Dummy alert - EN",
                        "hint": "dummy hint - EN",
                        "signature": "dummy signature - EN",
                        "paragraph": ""
                    }
                }
                """
                )
            ]
            for alarm in meteo_alarms:
                if self.poi_id in alarm.poi_ids:
                    _LOGGER.debug(
                        "found alarm for %i in %i", self.poi_id, alarm.alert_id
                    )

                    found_alarms.append(alarm)

        except json.decoder.JSONDecodeError:
            _LOGGER.exception("POI %i did not return a valid JSON", self.poi_id)
        except (ValueError, KeyError):
            _LOGGER.exception("did not satisfy expectations for POI %i", self.poi_id)
        else:
            return found_alarms

    async def _get_poi_data(self) -> POI:
        """Refresh the data we have from a POI."""
        try:
            res = await _api_wrapper("get", self.poi_url)
            try:
                return POI.model_validate(res)
            except ValidationError as e:
                msg = f"POI {self.poi_id} did not return a valid response"
                _LOGGER.exception("[%s] ❌ Validation error", self.poi_id)
                raise WetterAlarmApiError(poi_id=str(self.poi_id), msg=msg) from e
        except CannotConnectError:
            msg = f"POI {self.poi_id} did not return a valid response"
            _LOGGER.exception("Error validating the POI %s", self.poi_id)
            raise WetterAlarmApiError(poi_id=str(self.poi_id), msg=msg) from None

    async def refresh_poi(self) -> POI:
        """Central method to do a data refresh."""
        poi = await self._get_poi_data()
        alerts = await self._search_for_alerts()
        poi.alerts = alerts
        return poi


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
