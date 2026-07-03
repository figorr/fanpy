import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import *

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    prefix = entry.data.get(CONF_PREFIX, "ventilador")
    name = entry.data.get(CONF_NAME, prefix)
    num_speeds = entry.data.get(CONF_NUM_SPEEDS, 6)

    async_add_entities([
        FanSpeedSelect(hass, entry, prefix, name, num_speeds),
    ])


class FanSpeedSelect(SelectEntity):

    _attr_icon = "mdi:format-list-bulleted"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, prefix: str, name: str, num_speeds: int) -> None:
        self._hass = hass
        self._entry = entry
        self._prefix = prefix
        self._num_speeds = num_speeds
        self._attr_name = f"Fanpy {name} Velocidad"
        self._attr_unique_id = f"{CONF_ENTITY_PREFIX}_{prefix}_velocidad"
        self._attr_options = [str(i) for i in range(1, num_speeds + 1)]
        self._attr_current_option = self._attr_options[0]

    async def async_select_option(self, option: str) -> None:
        self._attr_current_option = option
        self.async_write_ha_state()

        await self._hass.services.async_call(
            "script", f"{self._prefix}_velocidad_{option}", {}, blocking=True
        )

        power_switch = f"switch.{CONF_ENTITY_PREFIX}_{self._prefix}_power"
        power_state = self._hass.states.get(power_switch)
        if power_state is None or power_state.state == "off":
            await self._hass.services.async_call(
                "switch", "turn_on", {"entity_id": power_switch}, blocking=True
            )
