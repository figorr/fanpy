import logging
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_MODE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv, selector

from .const import *

_LOGGER = logging.getLogger(__name__)


def _slugify(text: str) -> str:
    import re, unicodedata
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower().replace(" ", "_").replace("-", "_")
    text = re.sub(r"[^a-z0-9_]", "", text)
    return text


def _build_schemas(
    entry_data: Optional[Dict[str, Any]] = None,
    step: str = "user",
    num_speeds: int = 6,
):
    data = entry_data or {}

    if step == "user":
        return vol.Schema({
            vol.Required(CONF_MODE, default=data.get(CONF_MODE, CONF_MODE_HELPERS)): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[CONF_MODE_HELPERS, CONF_MODE_DIRECT],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        })

    if step == "area":
        return vol.Schema({
            vol.Required(CONF_AREA): selector.AreaSelector(),
        })

    if step == "direct_entity":
        return vol.Schema({
            vol.Required(CONF_ENTITY_FAN, default=data.get(CONF_ENTITY_FAN, "")): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="switch"),
            ),
            vol.Required(CONF_NUM_SPEEDS, default=data.get(CONF_NUM_SPEEDS, 1)): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=MIN_SPEEDS, max=MAX_SPEEDS, step=1,
                    mode=selector.NumberSelectorMode.DROPDOWN,
                )
            ),
        })

    if step == "direct_light":
        schema = {
            vol.Optional(CONF_HAS_LIGHT, default=data.get(CONF_HAS_LIGHT, True)): selector.BooleanSelector(),
        }
        if data.get(CONF_HAS_LIGHT, True):
            schema.update({
                vol.Optional(CONF_HAS_LIGHT_TEMPERATURE, default=data.get(CONF_HAS_LIGHT_TEMPERATURE, False)): selector.BooleanSelector(),
                vol.Optional(CONF_HAS_LIGHT_INTENSITY, default=data.get(CONF_HAS_LIGHT_INTENSITY, False)): selector.BooleanSelector(),
            })
        return vol.Schema(schema)

    if step == "helpers_speeds":
        return vol.Schema({
            vol.Required(CONF_NUM_SPEEDS, default=data.get(CONF_NUM_SPEEDS, 6)): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=MIN_SPEEDS, max=MAX_SPEEDS, step=1,
                    mode=selector.NumberSelectorMode.DROPDOWN,
                )
            ),
        })

    if step == "helpers_light":
        schema = {
            vol.Optional(CONF_HAS_LIGHT, default=data.get(CONF_HAS_LIGHT, True)): selector.BooleanSelector(),
        }
        if data.get(CONF_HAS_LIGHT, True):
            schema.update({
                vol.Optional(CONF_HAS_LIGHT_TEMPERATURE, default=data.get(CONF_HAS_LIGHT_TEMPERATURE, True)): selector.BooleanSelector(),
                vol.Optional(CONF_HAS_LIGHT_INTENSITY, default=data.get(CONF_HAS_LIGHT_INTENSITY, True)): selector.BooleanSelector(),
            })
        return vol.Schema(schema)

    if step == "helpers_broadlink":
        schema = {
            vol.Required(CONF_BROADLINK_DEVICE_ID, default=data.get(CONF_BROADLINK_DEVICE_ID, "")): selector.DeviceSelector(
                selector.DeviceSelectorConfig(domain="remote"),
            ),
            vol.Required(CONF_REMOTE_DEVICE, default=data.get(CONF_REMOTE_DEVICE, data.get(CONF_PREFIX, ""))): selector.TextSelector(),
            vol.Required(CONF_COMMAND_ON, default=data.get(CONF_COMMAND_ON, DEFAULT_COMMAND_ON)): selector.TextSelector(),
            vol.Required(CONF_COMMAND_OFF, default=data.get(CONF_COMMAND_OFF, DEFAULT_COMMAND_OFF)): selector.TextSelector(),
        }
        if data.get(CONF_HAS_LIGHT, True):
            schema.update({
                vol.Required(CONF_COMMAND_LUZ, default=data.get(CONF_COMMAND_LUZ, DEFAULT_COMMAND_LUZ)): selector.TextSelector(),
            })
            if data.get(CONF_HAS_LIGHT_TEMPERATURE, True):
                schema.update({
                    vol.Required(CONF_COMMAND_LUZ_CALIDA, default=data.get(CONF_COMMAND_LUZ_CALIDA, DEFAULT_COMMAND_LUZ_CALIDA)): selector.TextSelector(),
                    vol.Required(CONF_COMMAND_LUZ_FRIA, default=data.get(CONF_COMMAND_LUZ_FRIA, DEFAULT_COMMAND_LUZ_FRIA)): selector.TextSelector(),
                })
            if data.get(CONF_HAS_LIGHT_INTENSITY, True):
                schema.update({
                    vol.Required(CONF_COMMAND_INTENSIDAD_ALTA, default=data.get(CONF_COMMAND_INTENSIDAD_ALTA, DEFAULT_COMMAND_INTENSIDAD_ALTA)): selector.TextSelector(),
                    vol.Required(CONF_COMMAND_INTENSIDAD_BAJA, default=data.get(CONF_COMMAND_INTENSIDAD_BAJA, DEFAULT_COMMAND_INTENSIDAD_BAJA)): selector.TextSelector(),
                })
        return vol.Schema(schema)

    if step == "helpers_commands_velocidad":
        velocidad_schema = {}
        for i in range(1, num_speeds + 1):
            key = f"{CONF_COMMAND_VELOCIDAD_PREFIX}_{i}"
            default = f"{DEFAULT_COMMAND_VELOCIDAD_PREFIX}{i}"
            velocidad_schema[
                vol.Required(key, default=data.get(key, default))
            ] = selector.TextSelector()
        return vol.Schema(velocidad_schema)

    return vol.Schema({})


class FanpyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            mode = user_input[CONF_MODE]
            self._mode = mode
            return await self.async_step_area()

        schema = _build_schemas(step="user")
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_area(self, user_input=None):
        if user_input is not None:
            area = user_input[CONF_AREA]
            name = area.upper()
            prefix = _slugify(f"ventilador_{area}")

            await self.async_set_unique_id(prefix)
            self._abort_if_unique_id_configured()

            self._data = {
                CONF_AREA: area,
                CONF_NAME: name,
                CONF_PREFIX: prefix,
                CONF_MODE: self._mode,
            }

            if self._mode == CONF_MODE_DIRECT:
                return await self.async_step_direct_entity()
            return await self.async_step_helpers_speeds()

        schema = _build_schemas(self._data if hasattr(self, '_data') else {}, step="area")
        return self.async_show_form(step_id="area", data_schema=schema)

    async def async_step_direct_entity(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_direct_light()

        schema = _build_schemas(self._data, step="direct_entity")
        return self.async_show_form(step_id="direct_entity", data_schema=schema)

    async def async_step_direct_light(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(
                title=self._data[CONF_NAME],
                data=self._data,
            )

        schema = _build_schemas(self._data, step="direct_light")
        return self.async_show_form(step_id="direct_light", data_schema=schema)

    async def async_step_helpers_speeds(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_helpers_light()

        schema = _build_schemas(self._data, step="helpers_speeds")
        return self.async_show_form(step_id="helpers_speeds", data_schema=schema)

    async def async_step_helpers_light(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_helpers_broadlink()

        schema = _build_schemas(self._data, step="helpers_light")
        return self.async_show_form(step_id="helpers_light", data_schema=schema)

    async def async_step_helpers_broadlink(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_helpers_commands_velocidad()

        schema = _build_schemas(self._data, step="helpers_broadlink")
        return self.async_show_form(step_id="helpers_broadlink", data_schema=schema)

    async def async_step_helpers_commands_velocidad(self, user_input=None):
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(
                title=self._data[CONF_NAME],
                data=self._data,
            )

        num_speeds = self._data.get(CONF_NUM_SPEEDS, 6)
        schema = _build_schemas(self._data, step="helpers_commands_velocidad", num_speeds=num_speeds)
        return self.async_show_form(step_id="helpers_commands_velocidad", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return FanpyOptionsFlow(config_entry)


class FanpyOptionsFlow(config_entries.OptionsFlow):

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data = self.config_entry.data
        schema = vol.Schema({
            vol.Optional(CONF_HAS_LIGHT, default=data.get(CONF_HAS_LIGHT, True)): selector.BooleanSelector(),
            vol.Optional(CONF_HAS_LIGHT_TEMPERATURE, default=data.get(CONF_HAS_LIGHT_TEMPERATURE, True)): selector.BooleanSelector(),
            vol.Optional(CONF_HAS_LIGHT_INTENSITY, default=data.get(CONF_HAS_LIGHT_INTENSITY, True)): selector.BooleanSelector(),
        })
        return self.async_show_form(step_id="init", data_schema=schema)
