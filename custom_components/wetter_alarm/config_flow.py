"""Adds config flow for Blueprint."""

from __future__ import annotations

import logging
from typing import Any, ClassVar

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from custom_components.wetter_alarm.api import WetterAlarmApiError

from .api import WetterAlarmApiClient
from .const import (
    CONFIG_DATA_LANGUAGE,
    CONFIG_DATA_LANGUAGE_OPTIONS,
    CONFIG_POI_ID,
    CONFIG_POI_NAME,
    CONFIG_POIS,
    DOMAIN,
    LOGGER,
)

_LOGGER = logging.getLogger(__name__)


class WetterAlarmUserFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Blueprint."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL
    _pois: ClassVar[dict] = {}

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                poi_id = user_input.get(CONFIG_POI_ID, "")
                data_language = user_input.get(CONFIG_DATA_LANGUAGE, "en")

                client = WetterAlarmApiClient(poi_id, data_language)
                await client.async_validate_poi_id()

                poi_name = user_input.get(CONFIG_POI_NAME, "")

                return self.async_create_entry(
                    title="Wetter-Alarm",
                    data={
                        CONFIG_POIS: {(poi_name, poi_id)},
                        CONFIG_DATA_LANGUAGE: user_input.get(
                            CONFIG_DATA_LANGUAGE, "en"
                        ),
                    },
                )
            except WetterAlarmApiError as exception:
                LOGGER.warning(exception)
                _errors["base"] = exception.msg

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONFIG_POI_NAME,
                        default=(user_input or {}).get(CONFIG_POI_NAME, vol.UNDEFINED),
                    ): str,
                    vol.Required(
                        CONFIG_POI_ID,
                        default=(user_input or {}).get(CONFIG_POI_ID, vol.UNDEFINED),
                    ): int,
                    vol.Required(
                        CONFIG_DATA_LANGUAGE,
                        default=(user_input or {}).get(
                            CONFIG_DATA_LANGUAGE, vol.UNDEFINED
                        ),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=CONFIG_DATA_LANGUAGE_OPTIONS,
                            translation_key=CONFIG_DATA_LANGUAGE,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
            errors=_errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle reconfiguration of the integration."""
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])  # type: ignore[attr-defined]

        if user_input is not None:
            try:
                poi_name = user_input.get(CONFIG_POI_NAME, "")
                poi_id = user_input.get(CONFIG_POI_ID, "")
                data_language = user_input.get(CONFIG_DATA_LANGUAGE, "en")

                client = WetterAlarmApiClient(poi_id, data_language)
                await client.async_validate_poi_id()

                self.hass.config_entries.async_update_entry(
                    entry,
                    data={
                        CONFIG_POIS: {(poi_name, poi_id)},
                        CONFIG_DATA_LANGUAGE: data_language,
                    },
                )
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="Reconfigured")
            except WetterAlarmApiError as exception:
                LOGGER.warning(exception)

        current_data = entry.data if entry else {}
        _LOGGER.debug("Reconfigure entry %s", current_data)
        pois = list(current_data.get(CONFIG_POIS, []))
        _LOGGER.debug("Reconfigure pois %s", pois)

        prefill_poi_name = (user_input or {}).get(CONFIG_POI_NAME) or pois[0][0]
        prefill_poi_id = (user_input or {}).get(CONFIG_POI_ID) or pois[0][1]
        prefill_data_language = (user_input or {}).get(
            CONFIG_DATA_LANGUAGE
        ) or current_data.get(CONFIG_DATA_LANGUAGE, "en")

        _LOGGER.debug(
            "Reconfigure entry %s with prefill %s",
            current_data,
            {
                CONFIG_POI_NAME: prefill_poi_name,
                CONFIG_POI_ID: prefill_poi_id,
                CONFIG_DATA_LANGUAGE: prefill_data_language,
            },
        )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONFIG_POI_NAME,
                        default=(prefill_poi_name or vol.UNDEFINED),
                    ): str,
                    vol.Required(
                        CONFIG_POI_ID,
                        default=prefill_poi_id or vol.UNDEFINED,
                    ): int,
                    vol.Required(
                        CONFIG_DATA_LANGUAGE,
                        default=prefill_data_language or "en",
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=CONFIG_DATA_LANGUAGE_OPTIONS,
                            translation_key=CONFIG_DATA_LANGUAGE,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )
