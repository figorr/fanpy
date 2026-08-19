import voluptuous as vol

from homeassistant import config_entries

from .config_flow import _build_schemas
from .const import *


class FanpyOptionsFlowHandler(config_entries.OptionsFlow):

    VERSION = 1

    def __init__(self, config_entry):
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        mode = self._config_entry.data.get(CONF_MODE, CONF_MODE_REMOTE)
        if mode == CONF_MODE_DIRECT:
            return self.async_abort(reason="not_supported")

        self._pending_data = dict(self._config_entry.data)
        return await self.async_step_light_options()

    async def async_step_light_options(self, user_input=None):
        if user_input is not None:
            self._pending_data = {**self._pending_data, **user_input}
            if self._pending_data.get(CONF_HAS_LIGHT_TEMPERATURE, False):
                return await self.async_step_light_temp_modes()
            return await self._after_light_options()

        schema = _build_schemas(self._pending_data, step="helpers_light_options")
        return self.async_show_form(step_id="light_options", data_schema=schema)

    async def async_step_light_temp_modes(self, user_input=None):
        if user_input is not None:
            self._pending_data = {**self._pending_data, **user_input}
            return await self._after_light_options()

        schema = _build_schemas(self._pending_data, step="helpers_light_temp_modes")
        return self.async_show_form(step_id="light_temp_modes", data_schema=schema)

    async def _after_light_options(self):
        return await self.async_step_broadlink_config()

    async def async_step_broadlink_config(self, user_input=None):
        if user_input is not None:
            new_data = {**self._pending_data, **user_input}
            return await self._finish(new_data)

        data = self._pending_data
        num_speeds = data.get(CONF_NUM_SPEEDS, 6)
        schema = _build_schemas(data, step="helpers_broadlink", num_speeds=num_speeds)
        return self.async_show_form(step_id="broadlink_config", data_schema=schema)

    async def _finish(self, new_data):
        self.hass.config_entries.async_update_entry(
            self._config_entry,
            data=new_data,
        )
        from . import _generate_scripts_yaml
        await _generate_scripts_yaml(self.hass, self._config_entry)
        return self.async_create_entry(title="", data={})